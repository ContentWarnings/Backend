from .PosterPath import PosterPath
from ..databases.MovieTable import MovieTable
from ..cw.ContentWarning import ContentWarningReduced
from .MovieReduced import MovieReduced
from ..tmdb.tmdb import TMDB
import json
from pydantic import BaseModel
from typing import List


class MovieFull(BaseModel):
    @staticmethod
    def create(movie_id: int):
        """
        Constructor, pass in TMDB movie ID, returns None if fails, or a new MovieFull on success
        """
        response = TMDB.hit_api(f"movie/{movie_id}")

        if response.status_code != 200:
            return None

        json_map = json.loads(response.text)

        UNKNOWN_STR = "Unknown"
        UNKNOWN_INT = -1

        # mapping of TMDB's JSON response to our MovieFull fields
        # if the LHS is None, that means further parsing is needed or a different endpoint
        # is required to fill in the data, but we kept these fields in the mapping for posterity
        tmdb_to_movie_full = [
            ("id", "id"),
            ("imdb_id", "imdb"),
            (None, "cmid"),
            ("original_title", "title"),
            ("release_date", "release"),
            ("poster_path", "img"),
            ("backdrop_path", "backdrop"),
            (None, "mpa"),
            ("vote_average", "rating"),
            ("homepage", "url"),
            ("overview", "overview"),
            ("tagline", "tagline"),
            ("runtime", "runtime"),
            (None, "genres"),
            ("original_language", "lang"),
            (None, "cw"),
            (None, "similar"),
        ]

        movie_full_fields = dict()
        movie_full_fields_data_types = MovieFull.__dict__["__fields__"]
        is_field_an_int = lambda field: movie_full_fields_data_types[field].type_ is int

        for tmdb_field, movie_full_field in tmdb_to_movie_full:
            if tmdb_field is not None:
                try:
                    movie_full_fields[movie_full_field] = json_map[tmdb_field]
                except Exception:
                    movie_full_fields[movie_full_field] = (
                        UNKNOWN_INT
                        if is_field_an_int(movie_full_field)
                        else UNKNOWN_STR
                    )

        movie_full_fields["genres"] = []
        try:
            movie_full_fields["genres"] = [
                entry["name"] for entry in json_map["genres"]
            ]
        except Exception:
            pass

        movie_full_fields["cmid"] = -1
        movie_full_fields["mpa"] = TMDB.get_mpa_rating(movie_id)

        movie_full_fields["cw"] = [
            cw.to_ContentWarningReduced()
            for cw in MovieTable.get_all_ContentWarnings(movie_id)
            if cw is not None
        ]

        movie_full_fields["similar"] = []
        try:
            response = TMDB.hit_api(f"movie/{movie_id}/similar")
            if response.ok:
                js_map = json.loads(response.text)
                movie_full_fields["similar"] = [
                    MovieReduced.create(entry) for entry in js_map["results"]
                ]
        except Exception:
            pass

        # explicitly cast rating to float in case it's an integer value, or pydantic complains
        movie_full_fields["rating"] = float(movie_full_fields["rating"])

        # add prefix to poster paths
        for k in ["img", "backdrop"]:
            if movie_full_fields[k] is None or movie_full_fields[k] == "":
                continue
            movie_full_fields[k] = PosterPath.create_poster_link(movie_full_fields[k])

        # pydantic complains if fields are null
        for k, v in MovieFull.__fields__.items():
            if movie_full_fields[k] is None or (
                v.type_ is str and movie_full_fields[k] == ""
            ):
                if v.type_ is str:
                    movie_full_fields[k] = UNKNOWN_STR
                elif v.type_ is int or v.type_ is float:
                    movie_full_fields[k] = UNKNOWN_INT

        return MovieFull(**movie_full_fields)

    def jsonify(self):
        return self.__dict__

    id: int
    imdb: str
    cmid: int
    title: str
    release: str
    img: str
    backdrop: str
    mpa: str
    rating: float
    url: str
    overview: str
    tagline: str
    runtime: int
    genres: List[str]
    lang: str
    cw: List[ContentWarningReduced]
    similar: List[MovieReduced]

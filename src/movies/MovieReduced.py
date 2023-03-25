# References
# https://fastapi.tiangolo.com/tutorial/response-model/
# https://www.themoviedb.org/talk/5f3ef4eec175b200365ee352

from .get_unknown_genre_poster import get_unknown_poster_url
from ..databases.MovieTable import MovieTable
from .PosterPath import PosterPath
from ..tmdb.tmdb import TMDB
from enum import Enum
from pydantic import BaseModel
from typing import Dict, List


class MovieReducedFields(str, Enum):
    id_ascending = "id_ascending"
    id_descending = "id_descending"

    title_ascending = "title_ascending"
    title_descending = "title_descending"

    release_ascending = "release_ascending"
    release_descending = "release_descending"

    img_ascending = "img_ascending"
    img_descending = "img_descending"

    mpa_ascending = "mpa_ascending"
    mpa_descending = "mpa_descending"

    rating_ascending = "rating_ascending"
    rating_descending = "rating_descending"

    overview_ascending = "overview_ascending"
    overview_descending = "overview_descending"

    runtime_ascending = "runtime_ascending"
    runtime_descending = "runtime_descending"

    genres_ascending = "genres_ascending"
    genres_descending = "genres_descending"

    cw_ascending = "cw_ascending"
    cw_descending = "cw_descending"

    default_ascending = "default_ascending"
    default_descending = "default_descending"


def from_MovieReducedFields_to_raw_field(
    movie_reduced_field: MovieReducedFields,
) -> str:
    """
    Extracts raw MovieReduced field from the MovieReducedFields enum
    (basically removes underscore and suffix)

    Example: default_descending -> default
    """

    raw_val: str = movie_reduced_field.value
    return raw_val.split("_")[0]


class MovieReduced(BaseModel):
    @staticmethod
    def create(json_map: Dict[str, str]) -> None:
        """
        Use this as constructor when parsing TMDB JSON
        """
        UNKNOWN = "Unknown"

        def get_val(key: str) -> str:
            val = json_map.get(key, None)
            return UNKNOWN if (val is None or val == "") else val

        def get_mpa(id: int) -> str:
            mpa = TMDB.get_mpa_rating(id)
            return "Unknown" if mpa == "" else mpa

        image = get_val("poster_path")
        if image != UNKNOWN:
            image = PosterPath.create_poster_link(image)

        movie_id = int(json_map["id"])
        response = TMDB.hit_api(f"movie/{movie_id}")
        genres = []
        runtime = -1

        if response.ok:
            response = TMDB.jsonify_response(response)

            runtime = response.get("runtime")

            try:
                genres = [entry["name"] for entry in response["genres"]]
            except Exception:
                pass

        cw: List[str] = [
            cw_obj.name.value for cw_obj in MovieTable.get_all_ContentWarnings(movie_id) if cw_obj is not None
        ]

        if image == UNKNOWN:
            image = get_unknown_poster_url(genres)

        return MovieReduced(
            id=movie_id,
            title=get_val("title"),
            release=get_val("release_date"),
            img=image,
            mpa=get_mpa(json_map["id"]),
            rating=float(json_map.get("vote_average", -1)),
            overview=json_map["overview"],
            runtime=runtime,
            genres=genres,
            cw=cw,
        )

    def jsonify(self):
        return self.__dict__

    id: int
    title: str
    release: str
    img: str
    mpa: str
    rating: float
    overview: str
    runtime: int
    genres: List[str]
    cw: List[str]  # CW names

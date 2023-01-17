# References
# https://fastapi.tiangolo.com/tutorial/response-model/
# https://www.themoviedb.org/talk/5f3ef4eec175b200365ee352

from ..tmdb.tmdb import TMDB
from enum import Enum
from pydantic import BaseModel
from typing import Dict


class MovieReducedFields(str, Enum):
    id = "id"
    title = "title"
    release = "release"
    img = "img"
    mpa = "mpa"
    rating = "rating"


class MovieReduced(BaseModel):
    @staticmethod
    def create(json_map: Dict[str, str]) -> None:
        """
        Use this as constructor when parsing TMDB JSON
        """
        UNKNOWN = "Unknown"

        def get_val(key: str) -> str:
            val = json_map[key]
            return UNKNOWN if (val is None or val == "") else val

        def get_mpa(id: int) -> str:
            mpa = TMDB.get_mpa_rating(id)
            return "Unknown" if mpa == "" else mpa

        return MovieReduced(
            id=int(json_map["id"]),
            title=get_val("title"),
            release=get_val("release_date"),
            img=get_val("poster_path"),
            mpa=get_mpa(json_map["id"]),
            rating=float(json_map.get("vote_average", -1)),
        )

    def jsonify(self):
        return self.__dict__

    id: int
    title: str
    release: str
    img: str
    mpa: str
    rating: float

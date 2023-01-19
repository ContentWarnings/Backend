from ..movies.MovieFull import MovieFull
from ..cw.ContentWarning import ContentWarningReduced
from fastapi import APIRouter
from typing import List

get_movie_router = APIRouter()


@get_movie_router.get("/movie/{id}")
def get_cw(id: int) -> List[ContentWarningReduced]:
    movie = MovieFull.create(id)
    return movie if movie is None else movie.jsonify()

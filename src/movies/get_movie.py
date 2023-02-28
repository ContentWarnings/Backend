from ..movies.MovieFull import MovieFull
from ..cw.ContentWarning import ContentWarningReduced
from fastapi import APIRouter
from typing import List

get_movie_router = APIRouter()


@get_movie_router.get("/movie/{id}")
def get_movie(id: int) -> List[ContentWarningReduced]:
    """
    Given TMDB ID, returns MovieFull object, or None if not found
    """
    movie = MovieFull.create(id)
    return movie if movie is None else movie.jsonify()

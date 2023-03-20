from ..tmdb.genres import Genre
from fastapi import APIRouter
from fastapi.responses import FileResponse
from typing import List

get_unknown_genre_poster_router = APIRouter()


def get_unknown_poster_url(genres: List[str]):
    """
    Given a list of genre strings, returns a string representing a link to given unknown poster image
    """
    genre = Genre.TV_Movie.value  # generic looking poster
    if len(genres) > 0:
        genre = genres[0]

    return f"https://api.moviementor.app/genre_poster/{genre}"


@get_unknown_genre_poster_router.get("/genre_poster/{genre}")
def get_poster_img(genre: Genre):
    """
    Given a genre, return unknown movie poster
    """
    if genre == Genre.Disregard:
        genre = Genre.TV_Movie

    return FileResponse(f"./images/genre_posters/{genre.value}.png")

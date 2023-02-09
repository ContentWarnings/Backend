from fastapi.testclient import TestClient
import os

from .genres import Genre, GENRE_MAP


def test_genres():
    """
    Check sanity of genre enum
    """
    assert Genre.Action == "Action", "Invalid genre string for: Action"
    assert Genre.Adventure == "Adventure", "Invalid genre string for: Adventure"
    assert Genre.Animation == "Animation", "Invalid genre string for: Animation"
    assert Genre.Comedy == "Comedy", "Invalid genre string for: Comedy"
    assert Genre.Crime == "Crime", "Invalid genre string for: Crime"
    assert Genre.Documentary == "Documentary", "Invalid genre string for: Documentary"
    assert Genre.Drama == "Drama", "Invalid genre string for: Drama"
    assert Genre.Family == "Family", "Invalid genre string for: Family"
    assert Genre.Fantasy == "Fantasy", "Invalid genre string for: Fantasy"
    assert Genre.History == "History", "Invalid genre string for: History"
    assert Genre.Horror == "Horror", "Invalid genre string for: Horror"
    assert Genre.Music == "Music", "Invalid genre string for: Music"
    assert Genre.Mystery == "Mystery", "Invalid genre string for: Mystery"
    assert Genre.Romance == "Romance", "Invalid genre string for: Romance"
    assert (
        Genre.Science_Fiction == "Science Fiction"
    ), "Invalid genre string for: Science_Fiction"
    assert Genre.TV_Movie == "TV Movie", "Invalid genre string for: TV_Movie"
    assert Genre.Thriller == "Thriller", "Invalid genre string for: Thriller"
    assert Genre.War == "War", "Invalid genre string for: War"
    assert Genre.Western == "Western", "Invalid genre string for: Western"
    assert (
        Genre.Disregard == "Disregard"
    ), "Invalid genre string for: Disregard"  # when we don't care about genre


def test_genre_map():
    """
    Test sanity of genre map
    """
    assert GENRE_MAP.get(Genre.Action) == 28, "Invalid genre mapping for: Action"
    assert GENRE_MAP.get(Genre.Adventure) == 12, "Invalid genre mapping for: Adventure"
    assert GENRE_MAP.get(Genre.Animation) == 16, "Invalid genre mapping for: Animation"
    assert GENRE_MAP.get(Genre.Comedy) == 35, "Invalid genre mapping for: Comedy"
    assert GENRE_MAP.get(Genre.Crime) == 80, "Invalid genre mapping for: Crime"
    assert (
        GENRE_MAP.get(Genre.Documentary) == 99
    ), "Invalid genre mapping for: Documentary"
    assert GENRE_MAP.get(Genre.Drama) == 18, "Invalid genre mapping for: Drama"
    assert GENRE_MAP.get(Genre.Family) == 10751, "Invalid genre mapping for: Family"
    assert GENRE_MAP.get(Genre.Fantasy) == 14, "Invalid genre mapping for: Fantasy"
    assert GENRE_MAP.get(Genre.History) == 36, "Invalid genre mapping for: History"
    assert GENRE_MAP.get(Genre.Horror) == 27, "Invalid genre mapping for: Horror"
    assert GENRE_MAP.get(Genre.Music) == 10402, "Invalid genre mapping for: Music"
    assert GENRE_MAP.get(Genre.Mystery) == 9648, "Invalid genre mapping for: Mystery"
    assert GENRE_MAP.get(Genre.Romance) == 10749, "Invalid genre mapping for: Romance"
    assert (
        GENRE_MAP.get(Genre.Science_Fiction) == 878
    ), "Invalid genre mapping for: Science_Fiction"
    assert GENRE_MAP.get(Genre.TV_Movie) == 10770, "Invalid genre mapping for: TV_Movie"
    assert GENRE_MAP.get(Genre.Thriller) == 53, "Invalid genre mapping for: Thriller"
    assert GENRE_MAP.get(Genre.War) == 10752, "Invalid genre mapping for: War"
    assert GENRE_MAP.get(Genre.Western) == 37, "Invalid genre mapping for: Western"

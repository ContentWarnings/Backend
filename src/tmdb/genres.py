# References
# https://fastapi.tiangolo.com/tutorial/path-params/

from enum import Enum
from typing import Dict


class Genre(str, Enum):
    """
    Genres from TMDB API
    """

    Action = "Action"
    Adventure = "Adventure"
    Animation = "Animation"
    Comedy = "Comedy"
    Crime = "Crime"
    Documentary = "Documentary"
    Drama = "Drama"
    Family = "Family"
    Fantasy = "Fantasy"
    History = "History"
    Horror = "Horror"
    Music = "Music"
    Mystery = "Mystery"
    Romance = "Romance"
    Science_Fiction = "Science Fiction"
    TV_Movie = "TV Movie"
    Thriller = "Thriller"
    War = "War"
    Western = "Western"
    Disregard = "Disregard"  # when we don't care about genre


"""
Maps genres to their TMDB ID
"""
GENRE_MAP: Dict[Genre, int] = {
    Genre.Action: 28,
    Genre.Adventure: 12,
    Genre.Animation: 16,
    Genre.Comedy: 35,
    Genre.Crime: 80,
    Genre.Documentary: 99,
    Genre.Drama: 18,
    Genre.Family: 10751,
    Genre.Fantasy: 14,
    Genre.History: 36,
    Genre.Horror: 27,
    Genre.Music: 10402,
    Genre.Mystery: 9648,
    Genre.Romance: 10749,
    Genre.Science_Fiction: 878,
    Genre.TV_Movie: 10770,
    Genre.Thriller: 53,
    Genre.War: 10752,
    Genre.Western: 37,
}

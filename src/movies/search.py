# References
# https://fastapi.tiangolo.com/tutorial/bigger-applications/
# https://github.com/serverless/examples/blob/v3/aws-python-flask-dynamodb-api/app.py
# https://fastapi.tiangolo.com/tutorial/query-params/
# https://stackoverflow.com/questions/37343369/is-there-a-way-to-sort-custom-objects-in-a-custom-way-in-python
# https://docs.python.org/3/howto/sorting.html
# https://stackoverflow.com/questions/5618878/how-to-convert-list-to-string#5618893

from ..tmdb.tmdb import TMDB
from ..tmdb.genres import Genre, GENRE_MAP
from .MovieReduced import (
    MovieReduced,
    MovieReducedFields,
    from_MovieReducedFields_to_raw_field,
)
import boto3
from fastapi import APIRouter
import json
import os
import requests
from typing import List, Union

search_router = APIRouter()
dynamodb_client = boto3.client("dynamodb")

MOVIES_TABLE = os.environ["MOVIES_TABLE"]


def get_trending_movies(genre=Genre.Disregard, mm_page=1) -> requests.Response:
    """
    Returns trending movies from the last day, in JSON format
    """

    if genre == Genre.Disregard:
        if mm_page == 1:
            return TMDB.hit_api("trending/movie/day").json()
        else:
            return {"results": []}
    else:
        gid = GENRE_MAP[genre]

        return search_movie(
            query="", mm_page=mm_page, endpoint="discover/movie", genre_id=gid
        )


def search_movie(
    query: str, mm_page: int, endpoint: str = "search/movie", genre_id: int = None
):
    output = []

    pages_to_sum = 3

    # MovieMentor page -> TMDB page to start at
    tmdb_start_page = ((mm_page - 1) * pages_to_sum) + 1

    for subpage in range(0, pages_to_sum):
        tmdb_page = tmdb_start_page + subpage

        # Code reuse: genre filtering pagination and movie pagination is the same.
        if endpoint == "discover/movie":
            response = TMDB.hit_api(
                endpoint, f"&with_genres={genre_id}&page={tmdb_page}"
            )
        else:
            response = TMDB.hit_api(endpoint, f"&query={query}&page={tmdb_page}")

        json_map: dict = json.loads(response.text)
        for val in json_map["results"]:
            output.append(val)

        # Do not call additional pages if there are no more pages!
        if tmdb_page >= json_map["total_pages"]:
            break

    obj = {"results": output}

    return obj


@search_router.get("/search")
def search(
    q: Union[str, None] = None,
    p: int = 1,
    sort: MovieReducedFields = MovieReducedFields.default_ascending,
    genre: Genre = Genre.Disregard,
):
    """
    Return list of MovieReduced objects
    """

    # retrieve trending movies if query string is null or empty
    json_map: dict = (
        get_trending_movies(genre, p)
        if q is None or len(q.strip()) == 0
        else search_movie(q, p)
    )

    movies_list: List[MovieReduced] = []

    # return empty list if no results
    if len(json_map.get("results", [])) <= 0:
        # logging
        print("No results for TMDB search.")
        print(json_map)

        return {"results": []}

    for val in json_map["results"]:
        if genre != Genre.Disregard:
            if GENRE_MAP[genre] not in val["genre_ids"]:
                continue
        movies_list.append(MovieReduced.create(val))

    # sort if necessary
    if sort not in [
        MovieReducedFields.default_descending,
        MovieReducedFields.default_ascending,
    ]:
        movies_list = sorted(
            movies_list,
            key=lambda o: o.jsonify()[from_MovieReducedFields_to_raw_field(sort)],
        )

    # reverse list if sort is descending order
    if sort in [
        MovieReducedFields.id_descending,
        MovieReducedFields.title_descending,
        MovieReducedFields.release_descending,
        MovieReducedFields.img_descending,
        MovieReducedFields.mpa_descending,
        MovieReducedFields.rating_descending,
        MovieReducedFields.overview_descending,
        MovieReducedFields.runtime_descending,
        MovieReducedFields.genres_descending,
        MovieReducedFields.cw_descending,
        MovieReducedFields.default_descending,
    ]:
        movies_list.reverse()

    return {"results": [val.jsonify() for val in movies_list]}

# References
# https://fastapi.tiangolo.com/tutorial/bigger-applications/
# https://github.com/serverless/examples/blob/v3/aws-python-flask-dynamodb-api/app.py
# https://fastapi.tiangolo.com/tutorial/query-params/
# https://stackoverflow.com/questions/37343369/is-there-a-way-to-sort-custom-objects-in-a-custom-way-in-python
# https://docs.python.org/3/howto/sorting.html

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


def get_trending_movies() -> requests.Response:
    """
    Returns trending movies from the last day, in JSON format
    """
    return TMDB.hit_api("trending/movie/day")


@search_router.get("/search")
def search(
    q: Union[str, None] = None,
    p: int = 1,
    sort: MovieReducedFields = MovieReducedFields.default_ascending,
    genre: Genre = Genre.Disregard,
):
    response = (
        get_trending_movies()
        if q is None
        else TMDB.hit_api("search/movie", f"&query={q}&page={p}")
    )

    json_map: dict = json.loads(response.text)

    movies_list: List[MovieReduced] = []

    # return empty list if no results
    if "results" not in json_map.keys():
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

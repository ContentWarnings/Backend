from fastapi.testclient import TestClient
import os

from .tmdb import TMDB


def test_tmdb_manual_call():
    """
    Manual API call using TMDB wrapper.
    """
    trending = TMDB.hit_api("/trending/movie/day")
    assert trending.status_code == 200, "Could not load TMDB API"

    trending_data = trending.json()
    assert trending_data != None, "No JSON returned from TMDB API"

    assert trending_data.get("page") == 1, "Incorrect data returned"
    assert len(trending_data.get("results")) > 0, "Incorrect data returned; nothing is trending."



def test_tmdb_jsonify():
    """
    Test jsonify function
    """
    trending = TMDB.hit_api("/trending/movie/day")
    assert trending.status_code == 200, "Could not load TMDB API"

    trending_data = TMDB.jsonify_response(trending)
    assert trending_data.get("response", None) == None, "Valid TMDB call returned invalid response code"

    assert trending_data.get("page") == 1, "Incorrect data returned via jsonify"
    assert len(trending_data.get("results")) > 0, "Incorrect data returned via jsonify; nothing is trending."


def test_mpa_rating():
    """
    Test MPA string return.
    """
    rating = TMDB.get_mpa_rating(76600)
    assert rating == "PG-13", f"Rating returned is incorrect; expected 'PG-13', got '{rating}'."

from fastapi.testclient import TestClient
import os

from ..main import app

client = TestClient(app)


def test_get_search():
    """
    GET /search
    """

    # Get trending.
    data = client.get("/search")
    assert data.status_code == 200, "GET /search: Invalid response from server."

    data_json = data.json()
    assert data_json != None, "GET /search: No response for Trending."
    assert data_json != {}, "GET /search: Empty response for Trending."

    assert (
        data_json.get("results", None) != None
    ), "GET /search?q: Expected key 'results' is missing"
    assert (
        len(data_json.get("results")) > 0
    ), "GET /search?q: Expected key 'results' is empty"

    single_result = data_json.get("results")[0]

    assert (
        type(single_result.get("id")) == int
    ), "GET /search: Invalid data type for 'id'"
    assert (
        type(single_result.get("title")) == str
    ), "GET /search: Invalid data type for 'title'"
    assert (
        type(single_result.get("release")) == str
    ), "GET /search: Invalid data type for 'release'"
    assert (
        type(single_result.get("img")) == str
    ), "GET /search: Invalid data type for 'img'"
    assert (
        type(single_result.get("mpa")) == str
    ), "GET /search: Invalid data type for 'mpa'"
    assert (
        type(single_result.get("rating")) == float
    ), "GET /search: Invalid data type for 'rating'"


def test_get_search_q():
    """
    GET /search, with q defined
    """

    # Get if q set.
    data = client.get("/search?q=Avatar The Way of Water")
    assert data.status_code == 200, "GET /search?q: Invalid response from server."

    data_json = data.json()
    assert data_json != None, "GET /search?q: No response if q set.."
    assert data_json != {}, "GET /search?q: Empty response if q set.."

    assert (
        data_json.get("results", None) != None
    ), "GET /search?q: Expected key 'results' is missing"
    assert (
        len(data_json.get("results")) > 0
    ), "GET /search?q: Expected key 'results' is empty"

    single_result = data_json.get("results")[0]

    assert (
        type(single_result.get("id")) == int
    ), "GET /search?q: Invalid data type for 'id'"
    assert (
        type(single_result.get("title")) == str
    ), "GET /search?q: Invalid data type for 'title'"
    assert (
        type(single_result.get("release")) == str
    ), "GET /search?q: Invalid data type for 'release'"
    assert (
        type(single_result.get("img")) == str
    ), "GET /search?q: Invalid data type for 'img'"
    assert (
        type(single_result.get("mpa")) == str
    ), "GET /search?q: Invalid data type for 'mpa'"
    assert (
        type(single_result.get("rating")) == float
    ), "GET /search?q: Invalid data type for 'rating'"

    assert (
        single_result.get("id") == 76600
    ), f"GET /search?q: First result is incorrect. Expected 76600, got {single_result.get('id')}."


def test_get_search_genre():
    """
    GET /search, with genre defined
    """

    # Get if q set.
    data = client.get("/search?q=Mickey&genre=Animation")
    assert data.status_code == 200, "GET /search: Invalid response from server."

    data_json = data.json()
    assert data_json != None, "GET /search?q&genre: No response if q set.."
    assert data_json != {}, "GET /search?q&genre: Empty response if q set.."

    assert False, data_json

    assert (
        data_json.get("results", None) != None
    ), "GET /search?q: Expected key 'results' is missing"
    assert (
        len(data_json.get("results")) > 0
    ), "GET /search?q: Expected key 'results' is empty"

    single_result = data_json.get("results")[0]

    assert (
        type(single_result.get("id")) == int
    ), "GET /search?q&genre: Invalid data type for 'id'"
    assert (
        type(single_result.get("title")) == str
    ), "GET /search?q&genre: Invalid data type for 'title'"
    assert (
        type(single_result.get("release")) == str
    ), "GET /search?q&genre: Invalid data type for 'release'"
    assert (
        type(single_result.get("img")) == str
    ), "GET /search?q&genre: Invalid data type for 'img'"
    assert (
        type(single_result.get("mpa")) == str
    ), "GET /search?q&genre: Invalid data type for 'mpa'"
    assert (
        type(single_result.get("rating")) == float
    ), "GET /search?q&genre: Invalid data type for 'rating'"

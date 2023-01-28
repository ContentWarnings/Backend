from fastapi.testclient import TestClient
import os

from ..main import app
from ..cw import ContentWarning
from . import MovieReduced, MovieFull

client = TestClient(app)


def test_get_movie():
    """
    GET /movie/<id>
    """

    data = client.get("/movie/76600")  # Avatar 2
    assert data.status_code == 200, "GET /movie/<id>: Invalid response from server."

    data_json = data.json()
    assert data_json != None, "GET /movie/<id>: No response for movie."
    assert data_json != {}, "GET /movie/<id>: Empty response for movie."

    # Check if 'cw' stores a list of content warnings
    try:
        assert (
            type(ContentWarning(**(data_json.get("cw", None)[0]))) == ContentWarning
        ), "GET /movie/<id>: 'cw' missing or improper in response."
    except Exception as e:
        assert False, "GET /movie/<id>: 'cw' missing or improper in response."

    # Above for 'similar'
    try:
        assert (
            type(ContentWarning(**(data_json.get("similar", None)[0]))) == MovieReduced
        ), "GET /movie/<id>: 'similar' missing or improper in response."
    except Exception as e:
        assert False, "GET /movie/<id>: 'similar' missing or improper in response."

    # Above for [root]
    try:
        assert (
            type(ContentWarning(**(data_json))) == MovieFull
        ), "GET /movie/<id>: '[root]' missing or improper in response."
    except Exception as e:
        assert False, "GET /movie/<id>: '[root]' missing or improper in response."

    # Sanity-check values returned.
    assert (
        "avatar" in data_json.get("title", None).lower()
    ), "GET /movie/<id>: Invalid movie title."
    assert (
        data_json.get("mpa", None).lower() == "pg-13"
    ), "GET /movie/<id>: Invalid movie title."

    # assert (
    #     type(single_result.get("rating")) == list
    # ), "GET /search: Invalid data type for 'cw'"

    # Check if 'similar' stores a list of similar movies.


def test_post_movie():
    """
    POST /movie/<id>
    """

    # 1. get current list of CWs
    # 2. add CW
    # 3. see if CW was added properly

    pass

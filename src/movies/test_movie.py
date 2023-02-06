# References
# https://fastapi.tiangolo.com/tutorial/testing/

from fastapi.testclient import TestClient
import os
import uuid

from ..main import app
from ..cw import ContentWarning
from . import MovieReduced, MovieFull
from ..test_main import get_fake_session

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
        if data_json.get("cw", None):
            assert ContentWarning.ContentWarningReduced(
                **(data_json.get("cw", None)[0])
            ), "GET /movie/<id>: 'cw' missing in response."
    except Exception as e:
        assert False, "GET /movie/<id>: 'cw' improper in response."

    # Above for 'similar'
    try:
        assert MovieReduced.MovieReduced(
            **(data_json.get("similar", None)[0])
        ), "GET /movie/<id>: 'similar' missing in response."
    except Exception as e:
        assert False, "GET /movie/<id>: 'similar' improper in response."

    # Above for [root]
    try:
        assert MovieFull.MovieFull(
            **(data_json)
        ), "GET /movie/<id>: '[root]' missing in response."
    except Exception as e:
        assert False, "GET /movie/<id>: '[root]' improper in response."

    # Sanity-check values returned.
    assert (
        "avatar" in data_json.get("title", "").lower()
    ), "GET /movie/<id>: Invalid movie title."
    assert (
        data_json.get("mpa", "").lower() == "pg-13"
    ), "GET /movie/<id>: Invalid movie rating."

    # TODO: check if 'similar' stores a list of similar movies.


def test_post_movie():
    """
    POST /movie/<id>
    """

    cw_count = -1
    uuid_run = uuid.uuid4().hex

    print(f"POST /movie/<id>: Test run #{uuid_run}")

    # 1. get current list of CWs
    data_init = client.get("/movie/76600").json()  # Avatar 2
    cw_count = len(data_init.get("cw", []))
    print(data_init)

    # 2. add CW
    # cw_entry = ContentWarning.ContentWarning(
    #     name="Gun Violence",
    #     time=[120, 270],
    #     movie_id=42069,  # This should be ignored when sent to the API.
    #     desc="This is a placeholder content warning for testing purposes."
    # )
    # cw_data = cw_entry.jsonify()
    cw_data = {
        "name": "Gun Violence",
        "time": [[120, 270]],
        "id": "PLACEHOLDER14",
        "movie_id": 76600,
        "desc": f"This is a placeholder content warning for testing purposes. Test ID: {uuid_run}",
    }

    # Log in as a valid user and post movie.
    jwt = get_fake_session()
    data = client.post(
        "/movie/76600", json=cw_data, headers={"Authorization": f"Bearer {jwt}"}
    )
    print("-------------------")
    print(jwt)
    print(data.json())
    print("-------------------")

    # 3. see if CW was added properly
    data_fin = client.get("/movie/76600").json()  # Avatar 2
    print(data_fin)

    assert cw_count + 1 == len(
        data_fin.get("cw", [])
    ), "POST /movie/<id>: New content warning was not appended to the database."

    pulled_cw_data = data_fin.get("cw")[cw_count]

    assert (
        pulled_cw_data != None and pulled_cw_data != {}
    ), "POST /movie/<id>: New content warning was appended blank."

    assert (
        pulled_cw_data.get("name") == "Gun Violence"
    ), "POST /movie/<id>: Content warning added with incorrect classification."
    assert (
        pulled_cw_data.get("movie_id") != 42069
    ), "POST /movie/<id>: Movie ID was tampered with on addition (expected 76600, got 42069)."
    assert (
        pulled_cw_data.get("movie_id") == 76600
    ), f"POST /movie/<id>: Movie ID was appended incorrectly (expected 76600, got {pulled_cw_data.get('movie_id')})."
    assert (
        "This is a placeholder content warning for testing purposes."
        in pulled_cw_data.get("desc")
    ), "POST /movie/<id>: CW description added with incorrect description."
    assert pulled_cw_data.get("time") == [
        [
            120,
            270,
        ]
    ], "POST /movie/<id>: Timestamp tuple-like was added incorrectly."

# References
# https://fastapi.tiangolo.com/tutorial/testing/

from fastapi.testclient import TestClient
import os
import uuid

from requests import get

from ..main import app
from . import ContentWarning
from ..databases.ContentWarningTable import ContentWarningTable
from ..security.Sha256 import Sha256
from ..test_main import get_fake_session

client = TestClient(app)

IP_ADDRESS = get("https://ipapi.co/ip/").text


def test_get_cw():
    """
    GET /cw/<id>
    """
    # Change this to CW that matches the below tests.
    cw_id = "PLACEHOLDER"

    data = client.get("/cw/" + cw_id)
    assert data.status_code == 200, "GET /cw/<id>: Invalid response from server."

    data_json = data.json()
    assert data_json != None, "GET /cw/<id>: No response for CW."
    assert data_json != {}, "GET /cw/<id>: Empty response for CW."

    print(data_json)

    # Check if [root] is a content warning.
    try:
        assert ContentWarning.ContentWarningReduced(
            **(data_json)
        ), "GET /movie/<id>: '[root]' missing in response."
    except Exception as e:
        print(e)
        assert False, "GET /movie/<id>: '[root]' improper in response."

    # Sanity-check values returned.
    assert (
        data_json.get("name", "") == "Gun Violence"
    ), f"GET /cw/<id>: Invalid CW name (expected 'Gun Violence,' got '{data_json.get('name')}')."
    assert (
        data_json.get("desc", "")
        == "This is a placeholder content warning for testing purposes."
    ), f"GET /cw/<id>: Invalid CW description."
    assert (
        data_json.get("id", "") == cw_id
    ), f"GET /cw/<id>: Invalid CW ID (expected '{cw_id}, got '{data_json.get('id')}')."


def test_post_cw():
    """
    POST /cw/<id>
    """

    jwt = get_fake_session()

    # Check if fields were edited + deletion checks.
    helper_edit_cw({"name": "Ableism"}, jwt=jwt)
    helper_edit_cw({"time": [[90, 120]]}, jwt=jwt)
    helper_edit_cw({"desc": "This was changed!"}, jwt=jwt)
    helper_edit_cw({"time": [[90, 120]], "desc": "This was changed!"}, jwt=jwt)

    # Check to ensure we cannot edit other users' CWs
    uuid_illegal = uuid.uuid4().hex
    print(f"Illegal POST /cw/<id>: Adopting ID {uuid_illegal}")
    data = client.post(
        f"/cw/PLACEHOLDER",
        json={"desc": f"Illicit change: Test = {uuid_illegal}"},
        headers={"Authorization": f"Bearer {jwt}"},
    )
    assert (
        data.status_code != 200
    ), f"POST /cw/<id>: Able to edit another user's CW (Test = {uuid_illegal})"

    # Above, but not logged in.
    data = client.post(
        f"/cw/PLACEHOLDER/", json={"desc": f"Unauthed change: Test = {uuid_illegal}"}
    )
    assert (
        data.status_code != 200
    ), f"POST /cw/<id>: Able to edit another user's CW (Test = {uuid_illegal})"


def test_post_cw_upvote():
    """
    POST /cw/<id>/upvote
    """

    helper_cw_vote()


def test_post_cw_downvote():
    """
    POST /cw/<id>/upvote
    """

    helper_cw_vote(True)


def helper_edit_cw(edit_data, jwt=get_fake_session()):
    """
    Helper function to perform, and validate, CW edit operations.
    """
    uuid_run = uuid.uuid4().hex
    print(f"POST /cw/<id>: Adopting ID {uuid_run}")

    # Create CW for testing
    example_data = {
        "name": "Gun Violence",
        "time": [(60, 120)],
        "desc": f"POST /cw/ test run: {uuid_run}",
        "movie_id": 76600,
    }
    cw_data = client.post(
        "/movie", json=example_data, headers={"Authorization": f"Bearer {jwt}"}
    )
    cw_json = cw_data.json()
    cw_id = cw_json[-1].get("id", None)

    # Upvote (so there's something there.)
    helper_cw_vote(cw_id=cw_id)

    # we need a full object for POST, not only edit portions
    edit_data2 = example_data.copy()
    for k, v in edit_data.items():
        edit_data2[k] = v

    # Send HTTP request.
    data = client.post(
        f"/cw/{cw_id}", json=edit_data2, headers={"Authorization": f"Bearer {jwt}"}
    )

    assert (
        data.status_code < 400
    ), f"POST /cw/<id>: Invalid response from server (expected non-error, got {data.status_code})."

    # Data sanity check
    union = dict(edit_data, **example_data)
    new_obj = (
        ContentWarningTable.get_warning(cw_id).to_ContentWarningReduced().jsonify()
    )
    new_obj_full = ContentWarningTable.get_warning(cw_id).jsonify()
    new_obj["time"] = [[new_obj["time"][0][0], new_obj["time"][0][1]]]  # tuple -> list

    # delete ID since edit_data doesn't have it (CW Reduced), and change new_obj name to enum value
    del new_obj["id"]
    new_obj["name"] = new_obj["name"].value

    print(union)
    print("^^ expected ^^----vv actual vv")
    print(new_obj)

    # data should be different here
    assert union != new_obj, "POST /cw/<id>: Data did not change as expected."

    # Check if trust was changed in new_obj
    assert (
        new_obj_full.get("trust") == 0.0
    ), "POST /cw/<id>: Trust score not reset on modification."
    assert (
        len(new_obj_full.get("upvotes")) == 1
    ), "POST /cw/<id>: Upvote list not reset on modification."
    assert (
        len(new_obj_full.get("downvotes")) == 1
    ), "POST /cw/<id>: Downvote list not reset on modification."

    # Clean-up / deletion test (+ sanity checks).
    example_data["name"] = "None"  # set to None to delete CW
    data = client.post(
        f"/cw/{cw_id}",
        json=example_data,
        headers={"Authorization": f"Bearer {jwt}", "cf-connecting-ip": IP_ADDRESS},
    )

    assert data.status_code < 400, f"POST /cw/<id>: Invalid response from server."
    assert (
        ContentWarningTable.get_warning(cw_id) == None
    ), "POST /cw/<id>: Deletion of CW failed."


def helper_get_hashed_ip():
    """
    Helper function to get the hashed IP address.
    """
    return Sha256.hash(IP_ADDRESS)


def helper_cw_vote(is_downvote=False, cw_id="PLACEHOLDER2"):
    """
    Helper function that triggers an upvote (or downvote)
    """

    vote_type = "downvote" if is_downvote else "upvote"

    # Get original trust score
    old_trust = ContentWarningTable.get_warning(cw_id).jsonify().get("trust")

    data = client.get(
        f"/cw/{cw_id}/{vote_type}", headers={"cf-connecting-ip": IP_ADDRESS}
    )
    assert (
        data.status_code == 200
    ), f"GET /cw/<id>/{vote_type}: Invalid response from server."

    assert (
        data.json().get("response", None) != None
    ), f"GET /cw/<id>/{vote_type}: Lacking 'response' JSON field."

    new = ContentWarningTable.get_warning(cw_id).jsonify()
    new_trust = new.get("trust")

    if is_downvote:
        assert (
            old_trust > new_trust
        ), f"GET /cw/<id>/{vote_type}: Downvote failed: {old_trust} <= {new_trust}"
        assert helper_get_hashed_ip() in new.get(
            "downvotes"
        ), f"GET /cw/<id>/{vote_type}: Downvote failed: Hashed IP not logged in downvote list."
        assert helper_get_hashed_ip() not in new.get(
            "upvotes"
        ), f"GET /cw/<id>/{vote_type}: Downvote failed: Hashed IP erroneously logged in upvote list."

    else:
        assert (
            old_trust < new_trust
        ), f"GET /cw/<id>/{vote_type}: Upvote failed: {old_trust} >= {new_trust}"
        assert helper_get_hashed_ip() in new.get(
            "upvotes"
        ), f"GET /cw/<id>/{vote_type}: Upvote failed: Hashed IP not logged in upvote list."
        assert helper_get_hashed_ip() not in new.get(
            "downvotes"
        ), f"GET /cw/<id>/{vote_type}: Upvote failed: Hashed IP erroneously logged in downvote list."

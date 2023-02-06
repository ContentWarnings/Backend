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

    cw_id = "PLACEHOLDER2"


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


def helper_get_hashed_ip():
    ip_address = get("https://ipapi.co/ip/").text
    hashed_ip_address = Sha256.hash(ip_address)

    return hashed_ip_address


def helper_cw_vote(is_downvote=False):
    """
    Helper function that triggers an upvote (or downvote)
    """

    vote_type = "downvote" if is_downvote else "upvote"
    cw_id = "PLACEHOLDER2"

    # Get original trust score
    old_trust = ContentWarningTable.get_warning(cw_id).jsonify().get("trust")

    data = client.get(f"/cw/{cw_id}/{vote_type}")
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

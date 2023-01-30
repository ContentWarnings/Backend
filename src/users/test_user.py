# References;
# https://fastapi.tiangolo.com/tutorial/testing/

from fastapi.testclient import TestClient
import os
import uuid

from ..main import app
from ..cw import ContentWarning
from . import User, UserVerification
from ..databases.UserTable import UserTable

client = TestClient(app)

# Just a note: I do not think it's really possible to test the account creation flow because we
# send an validation email. That would require a lot of infrastructure to work properly, and
# it approaches diminishing marginal returns.
# The only way we can get it to work practically is if we 'stub out' email verification if running
# in a development environment.
# The same applies to the user deletion endpoints.


def test_everything_user_related_that_requires_a_login():
    """
    POST /user/register
    User verification logic.
    POST /auth/login
    GET /user
    POST /user (under various scenarios)
    """

    # Assign throwaway creds for this test case.
    user_test_uuid = uuid.uuid4().hex

    # POST /user/register
    creds = {
        "email": f"test_user_{user_test_uuid}@moviementor.com",
        "password": "WeAreInDevThisHardCodedCredIsProbablyFine1337!",
    }
    print(f"Adopting email {creds.get('email')} for this test...")
    register_data = client.post("/user/register", json=creds)

    # POST /auth/login (unverified)
    bad_login_data = client.post("/auth/login", json=creds)
    assert (
        bad_login_data.status_code == 401
    ), "POST /auth/login: Unverified user can request token."

    bad_login_json = bad_login_data.json()
    assert (
        bad_login_json.get("token", None) == None
    ), "POST /auth/login: Unverified user can obtain token (Expected HTTP 401)."

    # <Sorcery: Force-verify user>
    UserTable.set_user_to_verified(creds.get("email"))

    # POST /auth/login (verified)
    login_data = client.post("/auth/login", json=creds)
    assert (
        login_data.status_code != 401
    ), "POST /auth/login: User verification failed (Did not expect HTTP 401)."

    login_json = login_data.json()

    assert (
        login_json.get("token", None) != None
    ), "POST /auth/login: 'token' missing from response."
    assert (
        len(login_json.get("token", "")) < 10
    ), "POST /auth/login: 'token' is abnormally short. Is it empty?"

    # This is the authentication Bearer token.
    bearerToken = login_json.get("token", None)

    print("/// Logged in to Development environment successfully! ///")

    # GET /user
    data = client.get("/user", headers={"Authentication": f"Bearer {bearerToken}"})
    assert data.status_code == 200, "GET /user: Invalid response from server."

    data_json = data.json()
    assert data_json != None, "GET /user: No response for user."
    assert data_json != {}, "GET /user: Empty response for user."

    try:
        assert User.UserReduced(
            **(data_json)
        ), "GET /user: Response does not comply with UserReduced data type"
    except Exception:
        assert False, "GET /user: Response does not comply with UserReduced data type"

    # TODO: GET /user/export, if we keep that endpoint.

    # POST /user (email)
    email_tweaks = {"email": f"a_new_email_{user_test_uuid}@moviementor.com"}
    edit_user_data = client.post(
        "/user", json=email_tweaks, headers={"Authentication": f"Bearer {bearerToken}"}
    )

    # Do not allow emails to be changed willy-nilly; they need reverification. So old creds should still work.
    new_creds = {"email": email_tweaks.get("email"), "password": creds.get("password")}

    failed_login_data = client.post("/auth/login", json=new_creds)
    assert (
        failed_login_data.status_code != 200
    ), "POST /auth/login: Email was changed without re-verification (Expected HTTP 4xx, got HTTP 200)."
    assert (
        failed_login_data.get("token", None) == None
    ), "POST /auth/login: Email was changed without re-verification (token received)."

    # POST /user (bad password)
    password_tweaks = {"password": "hunter2"}
    edit_user_data = client.post(
        "/user",
        json=password_tweaks,
        headers={"Authentication": f"Bearer {bearerToken}"},
    )

    # We need to ban use of bad passwords
    new_creds = {
        "email": creds.get("email"),
        "password": password_tweaks.get("password"),
    }

    failed_login_data = client.post("/auth/login", json=new_creds)
    assert (
        failed_login_data.status_code != 200
    ), "POST /auth/login: Password illicitly weakened (Expected HTTP 4xx, got HTTP 200)."
    assert (
        failed_login_data.get("token", None) == None
    ), "POST /auth/login: Password illicitly weakened (token received)."

    # POST /user (good password)
    password_tweaks = {
        "password": "HereIsAnotherGoodPasswordWeShouldUse_98109!"
    }
    successful_login_data = client.post("/auth/login", json=new_creds)
    new_creds = {
        "email": creds.get("email"),
        "password": password_tweaks.get("password"),
    }
    assert (
        successful_login_data.status_code == 200
    ), f"POST /auth/login: Password not changed (expected HTTP 200, got {successful_login_data.status_code})"
    assert (
        successful_login_data.get("token", "") != ""
    ), "POST /auth/login: Password was not changed (token empty or not set)."

    # TODO: Delete user 

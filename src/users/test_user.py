# References;
# https://fastapi.tiangolo.com/tutorial/testing/

from fastapi.testclient import TestClient
import os
import uuid

from ..main import app
from ..cw import ContentWarning
from . import User, UserExported, UserVerification
from ..databases.UserVerificationTable import UserVerificationTable
from ..databases.UserTable import UserTable

client = TestClient(app)

# Note: These MUST be set to True; their existence is a convienence whilst developing the test cases.
do_check_status_codes = False
do_stringlike_checks = True


def NOtest_account_lifecycle():
    """
    POST /user/register (new)
    GET /user/verify
    POST /auth/login
    GET /user
    POST /user (under various scenarios)
    GET /user/password-reset-request
    POST /user/password-reset-op
    GET /user/delete-request
    POST /user/delete-op
    """

    # Assign throwaway creds for this test case.
    user_test_uuid = uuid.uuid4().hex

    # POST /user/register
    creds = {
        "email": f"test_user_{user_test_uuid}@moviementor.app",
        "password": "WeAreInDevThisHardCodedCredIsProbablyFine1337!",
    }
    print(f"Adopting email {creds.get('email')} for this test...")
    register_data = client.post("/user/register", json=creds)
    if do_stringlike_checks:
        assert (
            register_data.json().get("response", None) != None
        ), "GET /user/register: Lacking 'response' JSON field."

    # POST /auth/login (unverified)
    bad_login_data = client.post("/auth/login", json=creds)

    if do_check_status_codes:
        assert (
            bad_login_data.status_code == 401
        ), f"POST /auth/login: Unverified user can request token (expected HTTP 401, HTTP got {bad_login_data.status_code})"

    bad_login_json = bad_login_data.json()
    assert (
        bad_login_json.get("token", None) == None
    ), "POST /auth/login: Unverified user can obtain token (Expected HTTP 401)."

    # Test email verification flow.
    verify_code = {
        "email": creds.get("email"),
        "code": UserVerificationTable.get_user_verification_obj(
            creds.get("email")
        ).code,
    }
    verify_data = client.post("/user/verify", json=verify_code)

    ### REMOVE SOON! This is the force-verification logic.
    UserTable.set_user_to_verified(creds.get("email"))

    # POST /auth/login (verified)
    login_data = client.post("/auth/login", json=creds)

    if do_check_status_codes:
        assert (
            login_data.status_code != 401
        ), "POST /auth/login: User verification failed (Did not expect HTTP 401)."

    login_json = login_data.json()

    assert (
        login_json.get("token", None) != None
    ), "POST /auth/login: 'token' missing from response."
    assert (
        len(login_json.get("token", "")) > 10
    ), f"POST /auth/login: 'token' ({login_json.get('token')}) is abnormally short. Is it empty?"

    # This is the authentication Bearer token.
    bearerToken = login_json.get("token", None)

    print("/// Logged in to Development environment successfully! ///")

    # GET /user
    data = client.get("/user", headers={"Authorization": f"Bearer {bearerToken}"})
    assert data.status_code == 200, "GET /user: Invalid response from server."

    data_json = data.json()
    assert data_json != None, "GET /user: No response for user."
    assert data_json != {}, "GET /user: Empty response for user."

    try:
        assert UserExported.UserExported(
            **(data_json)
        ), "GET /user: Response does not comply with UserExported data type"
    except Exception:
        assert False, "GET /user: Response does not comply with UserExported data type"

    # POST /user (email)
    email_tweaks = {"email": f"a_new_email_{user_test_uuid}@moviementor.app"}
    edit_user_data = client.post(
        "/user", json=email_tweaks, headers={"Authorization": f"Bearer {bearerToken}"}
    )
    if do_stringlike_checks:
        assert (
            edit_user_data.json().get("response", None) != None
        ), "GET /user: Lacking 'response' JSON field."

    # Do not allow emails to be changed willy-nilly; they need reverification. So old creds should still work.
    new_creds = {"email": email_tweaks.get("email"), "password": creds.get("password")}

    failed_login_data = client.post("/auth/login", json=new_creds)

    if do_check_status_codes:
        assert (
            failed_login_data.status_code != 200
        ), "POST /auth/login: Email was changed without re-verification (Expected HTTP 4xx, got HTTP 200)."

    assert (
        failed_login_data.json().get("token", None) == None
    ), "POST /auth/login: Email was changed without re-verification (token received)."

    # POST /user (bad password)
    password_tweaks = {"password": "hunter2"}
    edit_user_data = client.post(
        "/user",
        json=password_tweaks,
        headers={"Authorization": f"Bearer {bearerToken}"},
    )

    # We need to ban use of bad passwords
    new_creds = {
        "email": creds.get("email"),
        "password": password_tweaks.get("password"),
    }

    failed_login_data = client.post("/auth/login", json=new_creds)

    if do_check_status_codes:
        assert (
            failed_login_data.status_code != 200
        ), "POST /auth/login: Password illicitly weakened (Expected HTTP 4xx, got HTTP 200)."
    assert (
        failed_login_data.json().get("token", None) == None
    ), "POST /auth/login: Password illicitly weakened (token received)."

    # POST /user (good password)
    password_tweaks = {"password": "HereIsAnotherGoodPasswordWeShouldUse_98109!"}
    new_creds = {
        "email": creds.get("email"),
        "password": password_tweaks.get("password"),
    }

    edit_user_data = client.post(
        "/user",
        json=new_creds,
        headers={"Authorization": f"Bearer {bearerToken}"},
    )

    ## Uncomment once <@ContentWarnings@github.com/Backend/issues/32> is fixed.
    ## This is the verification logic for the above.
    # successful_login_data = client.post("/auth/login", json=new_creds)
    #
    # if do_check_status_codes:
    #     assert (
    #         successful_login_data.status_code == 200
    #     ), f"POST /auth/login: Password not changed (expected HTTP 200, got {successful_login_data.status_code})"
    # assert (
    #     successful_login_data.json().get("token", "") != ""
    # ), "POST /auth/login: Password was not changed (token empty or not set)."

    # Outside password reset
    password_reset_data = client.get(
        f"/user/password-reset-request?email={creds.get('email')}"
    )
    if do_stringlike_checks:
        assert (
            password_reset_data.json().get("response", None) != None
        ), "GET /user/password-reset-request: Lacking 'response' JSON field."

    # Get reset code (this may need to change eventually, btw.)
    reset_code = UserVerificationTable.get_user_verification_obj(
        creds.get("email")
    ).code

    # (This first code attempt is wrong)
    password_reset_body = {
        "email": creds.get("email"),
        "new_password": creds.get("email") + "#changed",
        "code": reset_code + "-wrong",
    }
    password_commit_data = client.post(
        "/user/password-reset-op", json=password_reset_body
    )
    if do_check_status_codes:
        assert (
            password_commit_data.status_code != 200
        ), f"POST /user/password-reset-op: Password changed without a valid code (expected HTTP 4xx, got 200)"

    # (this second attempt is correct)
    password_reset_body = {
        "email": creds.get("email"),
        "new_password": creds.get("password") + "#changed",
        "code": reset_code,
    }
    password_commit_data = client.post(
        "/user/password-reset-op", json=password_reset_body
    )
    if do_check_status_codes:
        assert (
            password_commit_data.status_code == 200
        ), f"POST /user/password-reset-op: Password unchanged with a code (expected HTTP 200, got {password_commit_data.status_code})"
    if do_stringlike_checks:
        assert (
            password_commit_data.json().get("response", None) != None
        ), "GET /user/password-reset-op: Lacking 'response' JSON field."

    # Test user
    new_creds = {
        "email": creds.get("email"),
        "password": creds.get("password") + "#changed",
    }

    successful_login_data = client.post("/auth/login", json=new_creds)

    if do_check_status_codes:
        assert (
            successful_login_data.status_code == 200
        ), f"POST /auth/login: Externally-reset password not changed (expected HTTP 200, got {successful_login_data.status_code})"
    assert (
        successful_login_data.json().get("token", "") != ""
    ), "POST /auth/login: Externally-reset password was not changed (token empty or not set)."

    # Delete account.
    delete_request_data = client.get(
        f"/user/delete-request", headers={"Authorization": f"Bearer {bearerToken}"}
    )
    if do_stringlike_checks:
        assert (
            delete_request_data.json().get("response", None) != None
        ), "GET /user/delete-request: Lacking 'response' JSON field."

    # Get deletion code
    reset_code = UserVerificationTable.get_user_verification_obj(
        creds.get("email")
    ).deletion_code

    # (This first code attempt is wrong)
    delete_commit_data = client.get(
        "/user/delete-op?deletion_code=invalid-deletion-code",
        headers={"Authorization": f"Bearer {bearerToken}"},
    )
    if do_check_status_codes:
        assert (
            delete_commit_data.status_code != 200
        ), f"POST /user/delete-op: Delection occured without a valid code (expected HTTP 4xx, got 200)"

    # (this second attempt is correct)
    delete_commit_data = client.get(
        "/user/delete-op?deletion_code=" + reset_code,
        headers={"Authorization": f"Bearer {bearerToken}"},
    )
    if do_check_status_codes:
        assert (
            delete_commit_data.status_code == 200
        ), f"POST /user/delete-op: Password unchanged with a code (expected HTTP 200, got {delete_commit_data.status_code})"
    if do_stringlike_checks:
        assert (
            password_commit_data.json().get("response", None) != None
        ), "GET /user/delete-op: Lacking 'response' JSON field."

    # (Recall: new_creds = creds from last password reset)
    successful_login_data = client.post("/auth/login", json=new_creds)

    if do_check_status_codes:
        assert (
            successful_login_data.status_code == 404
        ), f"POST /auth/login: Account was not deleted (expected HTTP 404, got {successful_login_data.status_code})"

    assert (
        successful_login_data.json().get("token", None) == None
    ), "GET /auth/login: Logged in from a deleted account."

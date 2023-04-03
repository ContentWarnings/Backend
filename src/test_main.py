# References
# https://fastapi.tiangolo.com/tutorial/testing/
# https://automatetheboringstuff.com/2e/chapter7/

from fastapi.testclient import TestClient
import os
import re

from .main import app
from .security.JWT import JWT

client = TestClient(app)


def get_fake_session():
    """
    Instantly create a session for a fake user.
    """
    return JWT.create_encoded_jwt("test_user@moviementor.app", sudo=False)


# def test_create_fake_user():
#     # POST /user/register
# creds = {
#     "email": f"test_user@moviementor.app",
#     "password": "WeAreInDevThisHardCodedCredIsProbablyFine1337!",
# }
#     register_data = client.post("/user/register", json=creds)

#     UserTable.set_user_to_verified("test_user@moviementor.app")

#     print(register_data)
#     assert False, "Please comment out test_create_fake_user()"


def test_hello_world():
    """
    GET /
    """
    # major.minor.revision
    versioning_regex = re.compile(r"\d+.\d+.\d+")

    response = client.get("/")
    assert response.status_code == 200

    response_json = response.json()
    assert len(response_json) == 1
    assert "response" in response_json
    matches = versioning_regex.findall(response_json["response"])
    assert len(matches) == 1


def test_env_variables():
    """
    Test for required environment variables.
    """

    # Env key presence checks:
    keys = [
        "TMDB_API_KEY",
        "MOVIES_TABLE",
        "CW_TABLE",
        "USER_VERIFICATION_TABLE",
        "USER_TABLE",
        "JWT_SECRET",
        "JWT_ALGORITHM",
        "JWT_SUDO_LIFETIME",
        "JWT_USER_LIFETIME",
        "SENDGRID_API_KEY",
    ]
    for key in keys:
        try:
            assert os.environ[key], f"Missing env variable: {key}"
        except KeyError:
            assert False, f"Missing env variable: {key}"

        if "_TABLE" in key:
            assert (
                "-dev" not in key or "-prod" not in key
            ), "Environment missing from _TABLE key."

    # JWT sanity checks
    ONE_DAY = 86400

    assert (
        os.environ["JWT_ALGORITHM"] == "HS256"
    ), "Unexpected env variable: Why was the JWT algorithm changed?"
    assert len(os.environ["JWT_SECRET"]) >= 64, "JWT secret is too weak."
    assert (
        int(os.environ["JWT_USER_LIFETIME"]) <= ONE_DAY * 10
    ), "JWT lifetime is too long (User)"
    assert (
        int(os.environ["JWT_SUDO_LIFETIME"]) <= ONE_DAY
    ), "JWT lifetime is too long (Admin)"

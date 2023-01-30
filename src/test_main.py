# References
# https://fastapi.tiangolo.com/tutorial/testing/

from fastapi.testclient import TestClient
import os

from .main import app

client = TestClient(app)


def test_hello_world():
    """
    GET /
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"response": "Hello, world!"}


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
    assert (
        os.environ["JWT_ALGORITHM"] == "HS256"
    ), "Unexpected env variable: Why was the JWT algorithm changed?"
    assert len(os.environ["JWT_SECRET"]) >= 64, "JWT secret is too weak."
    assert (
        int(os.environ["JWT_USER_LIFETIME"]) <= 864000
    ), "JWT lifetime is too long (User)"
    assert (
        int(os.environ["JWT_SUDO_LIFETIME"]) <= 86400
    ), "JWT lifetime is too long (Admin)"

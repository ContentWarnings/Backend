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
    assert os.environ["TMDB_API_KEY"], "Missing env variable: TMDB_API_KEY"
    assert os.environ["MOVIES_TABLE"], "Missing env variable: MOVIES_TABLE"
    assert os.environ["CW_TABLE"], "Missing env variable: CW_TABLE"
    assert os.environ["USER_VERIFICATION_TABLE"], "Missing env variable: USER_VERIFICATION_TABLE"
    assert os.environ["USER_TABLE"], "Missing env variable: USER_TABLE"

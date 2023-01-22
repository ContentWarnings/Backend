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
    assert os.environ["TMDB_API_KEY"]
    assert os.environ["MOVIES_TABLE"]

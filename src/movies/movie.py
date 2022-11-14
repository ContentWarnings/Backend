# References
# https://fastapi.tiangolo.com/tutorial/bigger-applications/
# https://github.com/serverless/examples/blob/v3/aws-python-flask-dynamodb-api/app.py

from fastapi import APIRouter
import os
import boto3
import random

movie_router = APIRouter()
dynamodb_client = boto3.client("dynamodb")

MOVIES_TABLE = os.environ["MOVIES_TABLE"]


@movie_router.get("/movies/")
def movies_home():
    return {"movies": "home!"}


@movie_router.post("/movies/post/{movie_name}")
def post_movies(movie_name: str):
    dynamodb_client.put_item(
        TableName=MOVIES_TABLE,
        Item={"movieName": {"S": movie_name}, "dummyData": {"S": str(random.random())}},
    )


@movie_router.get("/movies/get/{movie_name}")
def get_movie(movie_name: str):
    result = dynamodb_client.get_item(
        TableName=MOVIES_TABLE, Key={"movieName": {"S": movie_name}}
    )
    item = result.get("Item")

    if not item:
        return {"error": "sorry"}

    return {"movie": str(item)}

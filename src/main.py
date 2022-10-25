# References
# https://github.com/jordaneremieff/serverless-mangum-examples/

from .movies import movie
from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()
app.include_router(movie.movie_router)


@app.get("/")
def hello():
    return {"hello": "world"}


# routes any requests to appropriate endpoint
handler = Mangum(app)

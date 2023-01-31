# References
# https://github.com/jordaneremieff/serverless-mangum-examples/

from .cw import edit_cw, get_cw, vote
from .movies import search, post_cw, get_movie
from .users import register_user, verify_user, login_user
from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()
app.include_router(search.search_router)
app.include_router(get_cw.get_cw_router)
app.include_router(post_cw.post_cw_router)
app.include_router(edit_cw.edit_cw_router)
app.include_router(get_movie.get_movie_router)
app.include_router(register_user.register_user_router)
app.include_router(verify_user.verify_user_router)
app.include_router(login_user.login_user_router)
app.include_router(vote.vote_router)


@app.get("/")
def hello():
    return {"hello": "world"}


handler = Mangum(app)

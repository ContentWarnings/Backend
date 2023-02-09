# References
# https://github.com/jordaneremieff/serverless-mangum-examples/

from .cw import edit_cw, get_cw, vote
from .movies import search, post_cw, get_movie
from .names import get_names
from .users import (
    delete_user_op,
    delete_user_request,
    edit_user,
    register_user,
    verify_user,
    login_user,
    get_user,
    password_reset_op,
    password_reset_request,
)
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
app.include_router(get_user.get_user_router)
app.include_router(password_reset_request.password_reset_request_router)
app.include_router(delete_user_request.delete_user_request_router)
app.include_router(delete_user_op.delete_user_op_router)
app.include_router(edit_user.edit_user_router)
app.include_router(password_reset_op.password_reset_op_router)
app.include_router(get_names.get_names_router)


@app.get("/")
def hello():
    return {"response": "Hello, world!"}


handler = Mangum(app)

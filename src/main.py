# References
# https://github.com/jordaneremieff/serverless-mangum-examples/
# https://fastapi.tiangolo.com/tutorial/cors/?h=%20cors#use-corsmiddleware

from .cw import edit_cw, get_cw, vote, has_voted
from .movies import search, post_cw, get_movie, get_unknown_genre_poster
from .names import get_names, get_desc
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
from fastapi.middleware.cors import CORSMiddleware
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
app.include_router(has_voted.has_voted_router)
app.include_router(get_desc.get_desc_router)
app.include_router(get_unknown_genre_poster.get_unknown_genre_poster_router)

# we're allowing any websites to hit this for now
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def version():
    """
    Returns current backend version: MAJOR.MINOR.REVISION
    """
    MAJOR = 1
    MINOR = 0
    REVISION = 0

    return {"response": f"{MAJOR}.{MINOR}.{REVISION}"}


handler = Mangum(app)

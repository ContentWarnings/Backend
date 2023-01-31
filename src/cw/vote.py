# References
# https://stackoverflow.com/questions/60098005/fastapi-starlette-get-client-real-ip
# https://fastapi.tiangolo.com/advanced/using-request-directly/

from ..databases.ContentWarningTable import ContentWarningTable
from ..security.Sha256 import Sha256
from fastapi import APIRouter, HTTPException, Request

vote_router = APIRouter()


def __vote_helper(cw_id: str, ip_address: str, upvote: bool = True) -> str:
    hashed_ip_address = Sha256.hash(ip_address)

    retval = (
        ContentWarningTable.upvote(cw_id, hashed_ip_address)
        if upvote
        else ContentWarningTable.downvote(cw_id, hashed_ip_address)
    )

    if type(retval) is tuple:
        raise HTTPException(retval[0], detail=retval[1])
    return retval


@vote_router.get("/cw/{id}/upvote")
def upvote(id: str, request: Request) -> str:
    return __vote_helper(id, request.client.host, upvote=True)


@vote_router.get("/cw/{id}/downvote")
def downvote(id: str, request: Request) -> str:
    return __vote_helper(id, request.client.host, upvote=False)

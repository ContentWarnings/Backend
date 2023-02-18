# References
# https://stackoverflow.com/questions/60098005/fastapi-starlette-get-client-real-ip
# https://fastapi.tiangolo.com/advanced/using-request-directly/

from ..cw.ContentWarning import ContentWarning
from ..databases.MovieTable import MovieTable
from ..databases.ContentWarningTable import ContentWarningTable
from ..security.IPAddress import IPAddress
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

    # if downvoting lowers trust enough & sufficient downvotes -> remove CW
    if not upvote:
        cw = ContentWarningTable.get_warning(cw_id)

        if cw is not None:
            if (
                cw.trust < ContentWarning.get_trust_deletion_threshold()
                and len(cw.downvotes)
                >= ContentWarning.get_num_downvotes_deletion_threshold()
            ):
                print(f"Trust of CW {cw.id} is too low. Deleting.")

                # yes, technically, we don't delete CW from user table, but the ID will refer
                # to nothing in the other tables, so it's effectively deleted. We can't delete
                # the CW reference in user table unless we scan every user in the database. This
                # will suffice for now, and runtime penalties are basically non-existent.
                MovieTable.delete_warning_from_movie(cw.movie_id, cw.id)
                ContentWarningTable.delete_warning(cw.id)

    return {"response": retval}


@vote_router.get("/cw/{id}/upvote")
def upvote(id: str, request: Request) -> str:
    return __vote_helper(id, IPAddress.get_ip_address(request), upvote=True)


@vote_router.get("/cw/{id}/downvote")
def downvote(id: str, request: Request) -> str:
    return __vote_helper(id, IPAddress.get_ip_address(request), upvote=False)

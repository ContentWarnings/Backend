from enum import Enum
from ..databases.ContentWarningTable import ContentWarningTable
from ..security.IPAddress import IPAddress
from ..security.Sha256 import Sha256
from fastapi import APIRouter, HTTPException, Request, status

has_voted_router = APIRouter()


class VotedOptions(str, Enum):
    upvoted = "upvoted"
    downvoted = "downvoted"
    nothing = "nothing"


@has_voted_router.get("/cw/{id}/has-voted")
def has_voted(id: str, request: Request):
    hashed_ip_address = Sha256.hash(IPAddress.get_ip_address(request))
    vote_option: VotedOptions = VotedOptions.nothing

    cw_obj = ContentWarningTable.get_warning(id)
    if cw_obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"CW {id} does not exist."
        )

    if hashed_ip_address in cw_obj.upvotes:
        vote_option = VotedOptions.upvoted
    elif hashed_ip_address in cw_obj.downvotes:
        vote_option = VotedOptions.downvoted

    return {"response": vote_option.value}

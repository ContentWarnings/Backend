# References
# https://fastapi.tiangolo.com/advanced/response-change-status-code/
# https://stackoverflow.com/questions/3825990/http-response-code-for-post-when-resource-already-exists
# https://fastapi.tiangolo.com/tutorial/security/first-steps/

import boto3
from ..security.Authentication import Authentication
from ..security.JWT import JWT
from ..security.ProfanityChecker import ProfanityChecker
from ..cw.ContentWarning import ContentWarningReduced, ContentWarningPosting
from ..databases.ContentWarningTable import ContentWarningTable
from ..databases.MovieTable import MovieTable
from ..databases.UserTable import UserTable
from fastapi import APIRouter, HTTPException, Request, Depends, status
from fastapi.security import OAuth2PasswordBearer
from typing import Dict, List, Optional

post_cw_router = APIRouter()
dynamodb_client = boto3.client("dynamodb")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@post_cw_router.post("/movie")
@Authentication.member
async def post_cw(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    root: ContentWarningPosting = None,
):
    """
    Post CW obj to databases (user, CW, movies), and return list of ContentWarningReduced
    """

    if root is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No content warning object given.",
        )

    ProfanityChecker.check_string(root.desc)

    email = JWT.get_email(token)

    # if user is low trust, act like we add their CW to DB, but secretly shadow ban by not
    # persisting any content from them. Simply return empty list in this case.
    low_trust_user_obj = UserTable.prune_downvoted_cws_and_update_low_trust(email)
    if low_trust_user_obj is not None and low_trust_user_obj.is_low_trust:
        print(f"User {email} is low trust, so discarding CW {root}.")
        return []

    # add cw to CW table
    full_cw = root.to_ContentWarningReduced().to_ContentWarning()
    result = ContentWarningTable.add_warning(full_cw)
    if type(result) is tuple:
        raise HTTPException(status_code=result[0], detail=result[1])

    # add cw UUID to user object
    user = UserTable.get_user(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User does not exist or invalid session token.",
        )
    user.contributions.append(full_cw.id)
    UserTable.edit_user(user)

    # add cw UUID to appropriate movie, creating entry if not inside movie table
    cw_ids: List[str] = MovieTable.add_warning_to_movie(full_cw.movie_id, full_cw.id)

    retval_cw_list: List[dict] = []
    for cw_id in cw_ids:
        warning = ContentWarningTable.get_warning(cw_id)
        if warning is not None:
            retval_cw_list.append(warning.to_ContentWarningReduced().jsonify())

    return retval_cw_list

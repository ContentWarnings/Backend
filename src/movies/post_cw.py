# References
# https://fastapi.tiangolo.com/advanced/response-change-status-code/
# https://stackoverflow.com/questions/3825990/http-response-code-for-post-when-resource-already-exists
# https://fastapi.tiangolo.com/tutorial/security/first-steps/

import boto3
from ..security.Authentication import Authentication
from ..security.JWT import JWT
from ..cw.ContentWarning import ContentWarningReduced
from ..databases.ContentWarningTable import ContentWarningTable
from ..databases.MovieTable import MovieTable
from ..databases.UserTable import UserTable
from fastapi import APIRouter, HTTPException, Request, Depends, status
from fastapi.security import OAuth2PasswordBearer
from typing import Dict, List, Optional

post_cw_router = APIRouter()
dynamodb_client = boto3.client("dynamodb")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@post_cw_router.post("/movie/{id}")
@Authentication.member
async def post_cw(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    id: int = None,
    root: ContentWarningReduced = None,
) -> Dict[ContentWarningReduced, Dict[str, str]]:
    if id is None:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No movie ID given."
        )

    if root is None:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No content warning object given.",
        )

    if id != root.movie_id:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"CW movie ID {root.movie_id} != endpoint movie ID {id}",
        )

    # add cw to CW table
    result = ContentWarningTable.add_warning(root.to_ContentWarning())
    if type(result) is tuple:
        raise HTTPException(status_code=result[0], detail=result[1])

    # add cw UUID to user object
    email = JWT.get_email(token)
    user = UserTable.get_user(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User does not exist or invalid session token.",
        )
    user.contributions.append(root.id)
    UserTable.edit_user(user)

    # add cw UUID to appropriate movie, creating entry if not inside movie table
    cw_ids: List[str] = MovieTable.add_warning_to_movie(id, root.id)

    retval_cw_list: List[dict] = []
    for cw_id in cw_ids:
        warning = ContentWarningTable.get_warning(cw_id)
        if warning is not None:
            retval_cw_list.append(warning.to_ContentWarningReduced().jsonify())

    return retval_cw_list

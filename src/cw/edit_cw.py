# References
# https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
# https://fastapi.tiangolo.com/tutorial/handling-errors/

from ..databases.MovieTable import MovieTable
from ..databases.ContentWarningTable import ContentWarningTable
from ..databases.UserTable import UserTable
from ..security.Authentication import Authentication
from ..security.JWT import JWT
from .ContentWarning import ContentWarningReduced, Nothing
from fastapi import APIRouter, Depends, Request, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from typing import Optional, Union

edit_cw_router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@edit_cw_router.post("/cw/{cw_id}")
@Authentication.member
async def edit_cw(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    cw_id: str = None,
    root: Union[ContentWarningReduced, Nothing] = None,
) -> ContentWarningReduced:
    if cw_id is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="No CW ID given.")

    if root is None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="No CW given for editing."
        )

    if type(root) is ContentWarningReduced and cw_id != root.id:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"CW endpoint ID {cw_id} != CW object ID {root.id}",
        )

    cw = ContentWarningTable.get_warning(cw_id)
    if cw is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"no CW exists with ID {cw_id}",
        )

    # if JSON body is passed in empty, we are to delete cw from CW table,
    # movies table, and user table, returning appropriate JSON on results
    if type(root) is Nothing:
        res1 = MovieTable.delete_warning_from_movie(cw.movie_id, cw.id)
        res2 = ContentWarningTable.delete_warning(cw_id)

        email = JWT.get_email(token)
        res3 = UserTable.delete_cw(email, cw_id)

        res1.update(res2)
        res1.update(res3)

        return res1

    # if JSON body is a valid cw, we edit it
    result = ContentWarningTable.edit_warning(root.to_ContentWarning())
    if type(result) is tuple:
        raise HTTPException(status_code=result[0], detail=result[1])
    return result.to_ContentWarningReduced().jsonify()

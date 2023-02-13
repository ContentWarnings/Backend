from ..databases.UserTable import UserTable
from ..users.UserExported import UserExported
from ..security.Authentication import Authentication
from ..security.JWT import JWT
from fastapi import APIRouter, Request, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Optional

get_user_router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@get_user_router.get("/user")
@Authentication.member
async def get_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
) -> UserExported:
    email = JWT.get_email(token)

    # before obtaining user, prune any dead CWs
    UserTable.prune_cw_list(email)

    return UserExported.create(UserTable.get_user_from_decoded_jwt(email)).jsonify()

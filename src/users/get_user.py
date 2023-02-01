from ..databases.UserTable import UserTable
from ..users.UserExported import UserExported
from ..security.Authentication import Authentication
from ..security.JWT import JWT
from fastapi import APIRouter, Request, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Optional

get_user_router = APIRouter()
oath2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@get_user_router.get("/user")
@Authentication.member
async def get_user(
    request: Request,
    token: Optional[str] = Depends(oath2_scheme),
) -> UserExported:
    user = UserTable.get_user_from_decoded_jwt(JWT.get_email(token))
    return UserExported.create(user).jsonify()

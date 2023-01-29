from ..security.JWT import JWT
from ..users.User import UserReduced
from ..databases.UserTable import UserTable
from ..security.Bcrypter import Bcrypter
from fastapi import APIRouter, HTTPException, status

login_user_router = APIRouter()


@login_user_router.post("/auth/login")
def login_user(incoming_user: UserReduced):
    user = UserTable.get_user(incoming_user.email)

    if user is None:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist or password does not match.",
        )

    if not user.verified:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error: User is not verified yet.",
        )

    if not Bcrypter.do_passwords_match(incoming_user.password, user.password):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User does not exist or password does not match.",
        )

    return {"result": JWT.create_encoded_jwt(incoming_user.email)}

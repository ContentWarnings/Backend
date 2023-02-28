from ..security.JWT import JWT
from ..users.User import UserReduced
from ..databases.UserTable import UserTable
from ..security.Bcrypter import Bcrypter
from fastapi import APIRouter, HTTPException, status

login_user_router = APIRouter()


@login_user_router.post("/auth/login")
def login_user(incoming_user: UserReduced):
    """
    Logs in a user, returns JWT string
    """
    user = UserTable.get_user(incoming_user.email)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist or password does not match.",
        )

    if not user.verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error: User is not verified yet.",
        )

    if not Bcrypter.do_passwords_match(incoming_user.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User does not exist or password does not match.",
        )

    return {"token": JWT.create_encoded_jwt(incoming_user.email)}

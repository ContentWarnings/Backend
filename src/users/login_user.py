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
            status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist."
        )

    if not user.verified:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error. User is not verified yet.",
        )

    if not Bcrypter.do_passwords_match(incoming_user.password, user.password):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password."
        )

    # TODO: return JWT instead of user info
    return user.jsonify()

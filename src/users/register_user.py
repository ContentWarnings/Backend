from ..databases.UserTable import UserTable
from ..databases.UserVerificationTable import UserVerificationTable
from ..users.User import UserReduced
from fastapi import APIRouter, HTTPException
import uuid

register_user_router = APIRouter()


@register_user_router.post("/user/register")
def register_user(user: UserReduced):
    user_verification_retval = UserVerificationTable.add_user(
        email=user.email, verif_code=str(uuid.uuid4())
    )
    if type(user_verification_retval) is tuple:
        raise HTTPException(
            status_code=user_verification_retval[0], detail=user_verification_retval[1]
        )

    add_user_retval = UserTable.add_user(user)
    if type(add_user_retval) is tuple:
        raise HTTPException(status_code=add_user_retval[0], detail=add_user_retval[1])

    # TODO: send verification code email to user

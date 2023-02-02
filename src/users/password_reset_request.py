from ..databases.UserTable import UserTable
from ..databases.UserVerificationTable import UserVerificationTable
from fastapi import APIRouter, HTTPException
import uuid

password_reset_request_router = APIRouter()


@password_reset_request_router.get("/user/password-reset-request")
def password_reset_request(email: str) -> str:
    # create a new verification code for the user
    retval = UserVerificationTable.add_new_verification_code_to_user(
        email, verif_code=str(uuid.uuid4())
    )
    if type(retval) is tuple:
        raise HTTPException(status_code=retval[0], detail=retval[1])

    # TODO: send email

    return "Check your email for a password reset code."

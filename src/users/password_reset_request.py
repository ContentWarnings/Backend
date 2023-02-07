from .CodeGenerator import CodeGenerator
from ..databases.UserTable import UserTable
from ..databases.UserVerificationTable import UserVerificationTable
from ..email.Emailer import Emailer
from fastapi import APIRouter, HTTPException

password_reset_request_router = APIRouter()


@password_reset_request_router.get("/user/password-reset-request")
def password_reset_request(email: str) -> str:
    # create a new verification code for the user
    pw_reset_code = CodeGenerator.create_new_verification_code()
    retval = UserVerificationTable.add_new_verification_code_to_user(
        email, verif_code=pw_reset_code
    )
    if type(retval) is tuple:
        raise HTTPException(status_code=retval[0], detail=retval[1])

    Emailer.send_code_via_email(
        email, pw_reset_code, Emailer.VerificationCode.PASSWORD_RESET
    )

    return "Check your email for a password reset code."

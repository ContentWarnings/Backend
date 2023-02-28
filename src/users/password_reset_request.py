from .CodeGenerator import CodeGenerator
from ..databases.UserTable import UserTable
from ..databases.UserVerificationTable import UserVerificationTable
from ..email.Emailer import Emailer
from fastapi import APIRouter, HTTPException

password_reset_request_router = APIRouter()


@password_reset_request_router.get("/user/password-reset-request")
def password_reset_request(email: str) -> str:
    """
    Sends password reset email, returns string of operation status
    """
    json_response = {"response": "Check your email for a password reset code."}

    # create a new verification code for the user
    pw_reset_code = CodeGenerator.create_new_verification_code()
    retval = UserVerificationTable.add_new_verification_code_to_user(
        email, verif_code=pw_reset_code
    )

    if type(retval) is tuple:
        UserVerificationTable.log_invalid_email()
        return json_response

    Emailer.send_code_via_email(
        email, pw_reset_code, Emailer.VerificationCode.PASSWORD_RESET
    )

    return json_response

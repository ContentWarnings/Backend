from .CodeGenerator import CodeGenerator
from ..databases.UserTable import UserTable
from ..databases.UserVerificationTable import UserVerificationTable
from ..email.Emailer import Emailer
from ..users.User import UserReduced
from fastapi import APIRouter, HTTPException, status

register_user_router = APIRouter()


@register_user_router.post("/user/register")
def register_user(user: UserReduced):
    # check if user already exists
    if UserTable.get_user(user.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Cannot use specified email."
        )

    Emailer.perform_email_validation(user.email)

    verif_code = CodeGenerator.create_new_verification_code()
    user_verification_retval = UserVerificationTable.add_user(
        email=user.email, verif_code=verif_code
    )
    if type(user_verification_retval) is tuple:
        raise HTTPException(
            status_code=user_verification_retval[0], detail=user_verification_retval[1]
        )

    add_user_retval = UserTable.add_user(user)
    if type(add_user_retval) is tuple:
        raise HTTPException(status_code=add_user_retval[0], detail=add_user_retval[1])

    Emailer.send_code_via_email(
        user.email, verif_code, Emailer.VerificationCode.VERIFICATION
    )

    return {"response": "Please check your email for a verification code."}

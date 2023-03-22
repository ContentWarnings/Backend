from .CodeGenerator import CodeGenerator
from ..email.Emailer import Emailer
from ..security.Bcrypter import Bcrypter
from ..users.User import UserEdit
from ..databases.UserTable import UserTable
from ..databases.UserVerificationTable import UserVerificationTable
from ..security.Authentication import Authentication
from ..security.JWT import JWT
from fastapi import APIRouter, HTTPException, Request, Depends, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional

edit_user_router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@edit_user_router.post("/user")
@Authentication.member
async def edit_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    incoming_user: UserEdit = None,
) -> str:
    """
    Edits user info, returning string of operation status
    """
    if incoming_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No 'incoming_user' object JSON passed in for edits.",
        )

    prev_user = UserTable.get_user_from_decoded_jwt(JWT.get_email(token))

    passwords_match = True
    if incoming_user.password is not None:
        passwords_match = Bcrypter.do_passwords_match(
            incoming_user.password, prev_user.password
        )

    emails_match = True
    if incoming_user.email is not None:
        emails_match = True if prev_user.email == incoming_user.email else False

    if passwords_match and emails_match:
        return {"response": "No changes to user information."}

    # 1. changing just password
    if emails_match:
        prev_user.password = Bcrypter.hash_password(incoming_user.password)
        UserTable.edit_user(prev_user)
        return {"response": "Edited password."}

    # before going on, check that specified email doesn't exist for another user
    if UserTable.get_user(incoming_user.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Error. Incoming user's new email cannot be used.",
        )

    # 2. changing email and maybe password, too
    # if email is changed, we add temporary email to user's database object until it's verified

    # first, verify new email
    Emailer.perform_email_validation(incoming_user.email)

    # if new email request is different from pending request, delete pending uv obj from database
    if (
        len(prev_user.new_pending_email) != 0
        and prev_user.new_pending_email != incoming_user.email
    ):
        UserVerificationTable.delete_user_verification_obj(prev_user.new_pending_email)

    verif_code = CodeGenerator.create_new_verification_code()

    # if the pending email already has a UV obj entry, update it, if not, add new entry to database
    if UserVerificationTable.get_user_verification_obj(incoming_user.email) is None:
        UserVerificationTable.add_user(incoming_user.email, verif_code=verif_code)
    else:
        UserVerificationTable.add_new_verification_code_to_user(
            incoming_user.email, verif_code=verif_code
        )

    # update current user with pending email and/or hashed password
    prev_user.new_pending_email = incoming_user.email
    if not passwords_match:
        prev_user.password = Bcrypter.hash_password(incoming_user.password)
    UserTable.edit_user(prev_user)

    Emailer.send_code_via_email(
        incoming_user.email,
        verif_code,
        Emailer.VerificationCode.VERIFICATION,
        prev_email=JWT.get_email(token),
    )

    return {
        "response": "Edited information. Check your email for a new verification code."
    }

from ..security.Bcrypter import Bcrypter
from ..users.User import UserReduced
from ..databases.UserTable import UserTable
from ..databases.UserVerificationTable import UserVerificationTable
from ..security.Authentication import Authentication
from ..security.JWT import JWT
from fastapi import APIRouter, HTTPException, Request, Depends, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
import uuid

edit_user_router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@edit_user_router.post("/user")
@Authentication.member
async def edit_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    incoming_user: UserReduced = None,
) -> str:
    if incoming_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No 'incoming_user' object JSON passed in for edits.",
        )

    prev_user = UserTable.get_user_from_decoded_jwt(JWT.get_email(token))

    passwords_match = Bcrypter.do_passwords_match(
        incoming_user.password, prev_user.password
    )
    emails_match = True if prev_user.email == incoming_user.email else False

    if passwords_match and emails_match:
        return "No changes to user information."

    # 1. changing just password
    if emails_match:
        prev_user.password = Bcrypter.hash_password(incoming_user.password)
        UserTable.edit_user(prev_user)
        return "Edited password."

    # before going on, check that specified email doesn't exist for another user
    if UserTable.get_user(incoming_user.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Error. Incoming user's new email cannot be used.",
        )

    # 2. changing email and maybe password, too
    # this means we basically clone old user into a new object, delete old object, and re-add "new"
    # user, because this means they need to go thru verification again if email changes
    UserVerificationTable.delete_user_verification_obj(prev_user.email)
    UserTable.delete_user(prev_user.email)

    updated_user = incoming_user.to_User()
    updated_user.contributions = prev_user.contributions  # copy over CW IDs

    # add to both tables
    UserVerificationTable.add_user(updated_user.email, verif_code=str(uuid.uuid4()))
    UserTable.add_user_obj(updated_user)

    return "Edited information. Check your email for a new verification code."

    # TODO: send another verification email

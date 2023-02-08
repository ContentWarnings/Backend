from ..users.User import User
from .UserVerification import UserVerificationReduced
from ..databases.UserTable import UserTable
from ..databases.UserVerificationTable import UserVerificationTable
from fastapi import APIRouter, HTTPException, status

verify_user_router = APIRouter()


def complete_new_email_verif_process(user: User) -> None:
    # persist any delete codes to new user, and also delete old uv object
    old_uv_obj = UserVerificationTable.get_user_verification_obj(user.email)
    UserVerificationTable.delete_user_verification_obj(user.email)
    UserVerificationTable.add_new_verification_code_to_user(
        user.new_pending_email, deletion_code=old_uv_obj.deletion_code
    )

    # change user's email to new one and reset pending email field; persist changes to database by
    # also deleting old user
    UserTable.delete_user(user.email)
    user.email = user.new_pending_email
    user.new_pending_email = ""

    # we're using edit function here so cw's, etc., are persisted
    UserTable.edit_user(user)


@verify_user_router.post("/user/verify")
def verify_user(uv_obj: UserVerificationReduced):
    """
    With input of specified user email and verification code, performs user verification
    """
    user_verification_obj = UserVerificationTable.get_user_verification_obj(
        uv_obj.email
    )

    if user_verification_obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {uv_obj.email} has not registered.",
        )

    # grab user from the database to ensure it's present
    user = UserTable.get_user(uv_obj.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User does not exist or password does not match.",
        )

    # user verifying existing email
    if user_verification_obj.code == uv_obj.code:
        UserTable.set_user_to_verified(uv_obj.email)
        return {"response": "Verification successful."}

    # user verifying a new email
    if len(user.new_pending_email) != 0:
        pending_email_verification_obj = (
            UserVerificationTable.get_user_verification_obj(user.new_pending_email)
        )
        if (
            pending_email_verification_obj is not None
            and pending_email_verification_obj.code == uv_obj.code
        ):
            UserTable.set_user_to_verified(uv_obj.email)
            complete_new_email_verif_process(user)
            return {"response": "New email verified. You may need to log in again."}

    # if user is already verified, exit
    if user.verified:
        return {"response": "User already verified."}

    # else, error
    raise HTTPException(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        detail=f"Incorrect verification code.",
    )

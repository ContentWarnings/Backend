from .UserVerification import UserVerificationReduced
from ..databases.UserTable import UserTable
from ..databases.UserVerificationTable import UserVerificationTable
from fastapi import APIRouter, HTTPException, status

verify_user_router = APIRouter()


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

    # if user is already verified, we're done
    if user.verified:
        return {"response": "User already verified."}

    if user_verification_obj.code == uv_obj.code:
        UserTable.set_user_to_verified(uv_obj.email)
    else:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=f"Incorrect verification code.",
        )

    return {"response": "Verification successful."}

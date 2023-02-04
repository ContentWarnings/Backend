from ..security.Bcrypter import Bcrypter
from ..users.UserPasswordReset import UserPasswordReset
from ..databases.UserTable import UserTable
from ..databases.UserVerificationTable import UserVerificationTable
from fastapi import APIRouter, HTTPException, status

password_reset_op_router = APIRouter()


@password_reset_op_router.post("/user/password-reset-op")
def password_reset_op(user_reset: UserPasswordReset) -> str:
    uv_obj = UserVerificationTable.get_user_verification_obj(user_reset.email)
    if uv_obj is None:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )

    if uv_obj.code != user_reset.code:
        return HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Incorrect password reset code.",
        )

    user = UserTable.get_user(user_reset.email)
    if user is None:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )

    user.password = Bcrypter.hash_password(user_reset.new_password)
    UserTable.edit_user(user)
    return "New password has been added."

from ..databases.UserTable import UserTable
from ..databases.UserVerificationTable import UserVerificationTable
from ..security.Authentication import Authentication
from ..security.JWT import JWT
from fastapi import APIRouter, HTTPException, Request, Depends, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional

delete_user_op_router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@delete_user_op_router.get("/user/delete-op")
@Authentication.member
async def delete_user_op(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    deletion_code: str = None,
) -> str:
    """
    Deletes user from tables (doesn't delete CW objects), returns string of operation status
    """
    if deletion_code is None or len(deletion_code) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No deletion code provided."
        )

    email = JWT.get_email(token)
    user_verification_obj = UserVerificationTable.get_user_verification_obj(email)
    if user_verification_obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {email} has not registered.",
        )

    if deletion_code != user_verification_obj.deletion_code:
        return {"response": "Incorrect deletion code."}

    # delete user from both tables
    UserVerificationTable.delete_user_verification_obj(email)
    response_msg = UserTable.delete_user(email)
    return {"response": response_msg}

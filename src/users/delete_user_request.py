from .CodeGenerator import CodeGenerator
from ..email.Emailer import Emailer
from ..databases.UserVerificationTable import UserVerificationTable
from ..security.Authentication import Authentication
from ..security.JWT import JWT
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Optional

delete_user_request_router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@delete_user_request_router.get("/user/delete-request")
@Authentication.member
async def delete_user_request(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
) -> str:
    email = JWT.get_email(token)
    deletion_code = CodeGenerator.create_new_verification_code()
    retval = UserVerificationTable.add_new_verification_code_to_user(
        email, deletion_code=deletion_code
    )
    if type(retval) is tuple:
        raise HTTPException(status_code=retval[0], detail=retval[1])

    Emailer.send_code_via_email(email, deletion_code, Emailer.VerificationCode.DELETION)

    return "Check your email for a deletion reset code."

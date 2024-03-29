# References
# https://github.com/mpdavis/python-jose
# https://stackoverflow.com/questions/64497615/how-to-add-a-custom-decorator-to-a-fastapi-route

from ..databases.UserTable import UserTable
import time
from functools import wraps
from jose import jwt
from typing import Optional
from fastapi import Request, HTTPException, status
from .util.options import Options


class Authentication:
    def __init__(self):
        super(Authentication, self).__init__

    def __ensure_user_is_in_database(email: str) -> None:
        """
        Tests whether user is currently present within database, raises Exception if not
        """
        if UserTable.get_user(email) is None:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Invalid user in auth token.",
            )

    def admin(func):
        @wraps(func)
        async def wrapper(request: Request, token: Optional[str], *args, **kwargs):
            # Validate auth.
            if not token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="You are not logged in.",
                )

            try:
                payload = jwt.decode(
                    token,
                    Options.get_secret(),
                    algorithms=Options.get_algorithm(),
                )
                Authentication.__ensure_user_is_in_database(payload["email"])
                is_admin: bool = payload.get("sudo", False)
                creation_date: float = payload.get("issued", -1)
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid token provided. Please log in again and try again.",
                )

            if not is_admin:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not an admin. If you think this is an error, please try logging in again.",
                )

            if time.time() > creation_date + Options.get_sudo_lifetime():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Session not new enough to verify admin status.",
                )

            return await func(request, token, *args, **kwargs)

        return wrapper

    def member(func):
        @wraps(func)
        async def wrapper_member(
            request: Request, token: Optional[str], *args, **kwargs
        ):
            # Validate auth.
            if not token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="You are not logged in.",
                )

            try:
                payload = jwt.decode(
                    token,
                    Options.get_secret(),
                    algorithms=Options.get_algorithm(),
                )
                Authentication.__ensure_user_is_in_database(payload["email"])
                creation_date: float = payload.get("issued", -1)
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid token provided. Please log in again and try again.",
                )

            if time.time() > creation_date + Options.get_user_lifetime():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Session expired.",
                )

            return await func(request, token, *args, **kwargs)

        return wrapper_member

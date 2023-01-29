# References
# https://github.com/mpdavis/python-jose
# https://stackoverflow.com/questions/64497615/how-to-add-a-custom-decorator-to-a-fastapi-route

import time
from functools import wraps
from jose import jwt
from typing import Optional
from fastapi import Request, HTTPException, status
from .util.options import Options


class Authentication:
    def __init__(self):
        super(Authentication, self).__init__

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
                    detail="Session not new enough to verify admin status. Unlike normal log-in, non-bot sudoer sessions only last a day.",
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

                creation_date: float = payload.get("issued", -1)
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid token provided. Please log in again and try again.",
                )

            if time.time() > creation_date + Options.get_user_lifetime():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Session expired. Sessions last for about fifteen weeks.",
                )

            return await func(request, token, *args, **kwargs)

        return wrapper_member

# References
# https://statisticsglobe.com/get-unix-timestamp-current-date-time-python
# https://learning.postman.com/docs/sending-requests/authorization/#bearer-token

from fastapi import HTTPException, status
import time
from jose import jwt
from typing import Union

from .util.options import Options


class JWT:
    @staticmethod
    def create_encoded_jwt(email: str, sudo: bool = False, issued: int = None) -> str:
        """
        Returns a JWT with specified email, whether user is an admin (true/false), and
        designated timestamp (defaults to current time)
        """
        token = {
            "email": email,
            "sudo": sudo,
            "issued": issued if issued is not None else time.time(),  # UNIX timestamp
        }

        return jwt.encode(
            token,
            Options.get_secret(),
            algorithm=Options.get_algorithm(),
        )

    @staticmethod
    def get_email(encoded_jwt: str) -> str:
        """
        Decodes JWT to extract email, if exists, otherwise raises exception
        """
        try:
            payload = jwt.decode(
                encoded_jwt,
                Options.get_secret(),
                algorithms=Options.get_algorithm(),
            )
            return payload["email"]
        except Exception:
            raise HTTPException(
                status.HTTP_406_NOT_ACCEPTABLE, detail="Error with auth token."
            )

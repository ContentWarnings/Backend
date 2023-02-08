from pydantic import BaseModel


class UserVerification(BaseModel):
    """
    Objects stored in our user verification database
    """

    email: str
    code: str  # verification code, UUID
    deletion_code: str  # UUID

    def jsonify(self):
        return self.__dict__


class UserVerificationReduced(BaseModel):
    """
    Objects passed in via frontend for verifying
    """

    email: str
    code: str

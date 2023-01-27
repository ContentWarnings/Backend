from pydantic import BaseModel


class UserVerification(BaseModel):
    """
    Objects stored in our user verification database
    """

    email: str
    code: str  # verification code, UUID

    def jsonify(self):
        return self.__dict__

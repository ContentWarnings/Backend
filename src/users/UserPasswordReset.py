from pydantic import BaseModel


class UserPasswordReset(BaseModel):
    """
    Object for resetting a user's password
    """

    email: str
    new_password: str
    code: str  # verification code, UUID

from pydantic import BaseModel
from typing import List, Union


class User(BaseModel):
    """
    User objects stored in our database
    """

    def to_UserReduced(self):
        """
        Creates a new UserReduced object from self
        """
        return UserReduced(email=self.email, password=self.password)

    email: str
    new_pending_email: str  # if user requests new email, populate it here until verified
    password: str  # salted and bcrypt-hashed
    verified: bool  # email verified or not
    contributions: List[str]  # UUIDs for content warnings submitted

    def jsonify(self):
        return self.__dict__


class UserReduced(BaseModel):
    """
    User objects passed in from frontend
    """

    def to_User(self):
        """
        Creates a new User object from self.
        """
        return User(
            email=self.email,
            new_pending_email="",
            password=self.password,
            verified=False,
            contributions=list(),
        )

    email: str
    password: str

    def jsonify(self):
        return self.__dict__


class UserEdit(BaseModel):
    """
    Objects passed in for editing.
    """

    email: Union[str, None]
    password: Union[str, None]

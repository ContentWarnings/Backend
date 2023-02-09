from pydantic import BaseModel
from typing import List


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
            password=self.password,
            verified=False,
            contributions=list(),
        )

    email: str
    password: str

    def jsonify(self):
        return self.__dict__

from ..databases.ContentWarningTable import ContentWarningTable
from .User import User
from ..cw.ContentWarning import ContentWarningReduced
from pydantic import BaseModel
from typing import List


class UserExported(BaseModel):
    """
    User objects we return to our frontend
    """

    email: str
    contributions: List[ContentWarningReduced]

    @staticmethod
    def create(user: User):
        """
        Creates a new UserExported object from a given User
        """
        cw_reduced_list: List[ContentWarningReduced] = []
        for cw_id in user.contributions:
            cw = ContentWarningTable.get_warning(cw_id)
            if cw is not None:
                cw_reduced_list.append(cw.to_ContentWarningReduced())

        return UserExported(
            email=user.email,
            contributions=cw_reduced_list,
        )

    def jsonify(self):
        return self.__dict__

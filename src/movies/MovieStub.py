from ..cw.ContentWarning import ContentWarning
from pydantic import BaseModel
from typing import List


class MovieStub(BaseModel):
    """
    Bare bones objects stored in movie database
    """

    id: int
    cmid: int
    cw: List[str]  # UUIDs for content warnings

    def jsonify(self):
        return self.__dict__

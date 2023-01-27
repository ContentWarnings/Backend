# References
# https://stackoverflow.com/questions/64807163/importerror-cannot-import-name-from-partially-initialized-module-m

from pydantic import BaseModel
from typing import List, Set, Tuple


class Nothing(BaseModel):
    """
    Represents empty JSON body for certain DELETE calls
    """

    None


class ContentWarningReduced(BaseModel):
    """
    These are the objects which our API receives via calls, since we do not give access to
    upvotes, downvotes, and trust score. Hence, this is a reduced version of our DB schema.
    """

    def to_ContentWarning(
        self, trust: int = 0, upvotes: Set[str] = None, downvotes: Set[str] = None
    ):
        """
        Creates a new ContentWarning object from self
        """

        # sets cannot be empty, else Dynamo will complain
        if upvotes == None:
            upvotes = {""}
        if downvotes == None:
            downvotes = {""}

        return ContentWarning(
            name=self.name,
            id=self.id,
            movie_id=self.movie_id,
            time=self.time,
            desc=self.desc,
            trust=trust,
            upvotes=upvotes,
            downvotes=downvotes,
        )

    def jsonify(self):
        return self.__dict__

    name: str
    id: str  # UUID
    movie_id: int  # TMDB ID
    time: List[Tuple[int, int]]
    desc: str


class ContentWarning(BaseModel):
    def to_ContentWarningReduced(self) -> ContentWarningReduced:
        """
        Creates a new ContentWarningReduced object from self
        """
        return ContentWarningReduced(
            name=self.name,
            id=self.id,
            movie_id=self.movie_id,
            time=self.time,
            desc=self.desc,
        )

    def jsonify(self):
        return self.__dict__

    name: str
    id: str  # UUID
    movie_id: int  # TMDB ID
    time: List[Tuple[int, int]]
    desc: str

    # hidden fields
    trust: int
    upvotes: Set[str]
    downvotes: Set[str]

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
        self, trust: float = 0, upvotes: Set[str] = None, downvotes: Set[str] = None
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

    def calculate_trust_score(self) -> None:
        """
        Calculates and sets internal trust score
        """
        LOWEST_TRUST_SCORE = 0.0
        HIGHEST_TRUST_SCORE = 1.0

        def calculate_num_votes(s: Set[str]) -> int:
            if s is None:
                return 0
            if "" in s:
                return len(s) - 1
            return len(s)

        upvote_num = calculate_num_votes(self.upvotes)
        downvote_num = calculate_num_votes(self.downvotes)

        numerator = upvote_num
        denominator = upvote_num + downvote_num

        if denominator == 0:  # avoid divide by zero
            if numerator == 0:  # no upvotes and no downvotes
                self.trust = LOWEST_TRUST_SCORE
            else:  # all upvotes!
                self.trust = HIGHEST_TRUST_SCORE
        else:
            self.trust = numerator / denominator

    name: str
    id: str  # UUID
    movie_id: int  # TMDB ID
    time: List[Tuple[int, int]]
    desc: str

    # hidden fields
    trust: float  # continuous scale on [0, 1]
    upvotes: Set[str]  # hashed IP addresses
    downvotes: Set[str]  # hashed IP addresses

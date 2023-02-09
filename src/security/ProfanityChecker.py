# References
# https://github.com/snguyenthanh/better_profanity

from fastapi import HTTPException, status
from better_profanity import profanity


class ProfanityChecker:
    @staticmethod
    def check_string(s: str) -> None:
        """
        Determines whether a string is free of profanity, if not, throws Exception
        """
        if profanity.contains_profanity(s):
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="String is profane."
            )

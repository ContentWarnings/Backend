from pydantic import BaseModel
from typing import List, Tuple


class StreamingInfo(BaseModel):
    """
    Holds streaming info for a movie
    """

    # index 0 holds the provider along with type (rent/buy/etc.) in format: "<provider> - <type>"
    # index 1 holds provider logo URL
    providers: List[Tuple[str, str]]

    # deep link to movie's TMDB page with deep links to other streaming services
    tmdb_link: str

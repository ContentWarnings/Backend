# References
# https://www.themoviedb.org/talk/5f3ef4eec175b200365ee352


class PosterPath:
    """
    Bundle of helpful poster operations for TMDB API
    """

    @staticmethod
    def create_poster_link(poster_suffix: str) -> str:
        """
        Given the poster suffix from a hit to TMDB API, returns full url string for the asset
        """
        return "https://image.tmdb.org/t/p/original" + poster_suffix

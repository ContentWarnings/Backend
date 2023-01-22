# References
# https://stackoverflow.com/questions/4528099/convert-json-string-to-dict-using-python
# https://medium.datadriveninvestor.com/accessing-github-secrets-in-python-d3e758d8089b
# https://www.themoviedb.org/talk/5d588e585cc11d00125ff1f1

import json
import requests
import os


class TMDB:
    """
    Holds a bunch of methods to perform TMDB API operations
    """

    __TMDB_API_KEY = os.environ["TMDB_API_KEY"]

    @staticmethod
    def hit_api(path: str, query: str = "") -> requests.Response:
        """
        Hits the TMDB API with corresponding path and query param string, returns Response object
        """

        api = (
            f"https://api.themoviedb.org/3/{path}?api_key={TMDB.__TMDB_API_KEY}{query}"
        )
        response = requests.get(api)

        return response

    @staticmethod
    def jsonify_response(response: requests.Response) -> str:
        """
        Returns either response's JSON or an error JSON message
        """
        return response.json() if response.ok else {"response": "error"}

    @staticmethod
    def get_mpa_rating(id: int) -> str:
        """
        Returns the mpa rating for a film, if exists
        """
        response = TMDB.hit_api(f"movie/{id}", "&append_to_response=release_dates")

        if not response.ok:
            return "Unknown"

        results = TMDB.jsonify_response(response).get("release_dates").get("results")

        rating = "Unknown"
        for item in results:
            if item["iso_3166_1"] == "US":
                try:
                    # Sometimes, there can be multiple releases per region.
                    # Example: 76600 (Avatar: The Way of Water)
                    for release in item["release_dates"]:
                        if release["certification"] != "":
                            rating = release["certification"]
                            break
                except Exception:
                    pass
                break

        return rating

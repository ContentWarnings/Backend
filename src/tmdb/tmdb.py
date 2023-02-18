# References
# https://stackoverflow.com/questions/4528099/convert-json-string-to-dict-using-python
# https://medium.datadriveninvestor.com/accessing-github-secrets-in-python-d3e758d8089b
# https://www.themoviedb.org/talk/5d588e585cc11d00125ff1f1
# https://pypi.org/project/python-dotenv/

from ..movies.PosterPath import PosterPath
from ..movies.StreamingInfo import StreamingInfo
from dotenv import load_dotenv
import json
import requests
import os
from typing import List, Union, Tuple


class TMDB:
    """
    Holds a bunch of methods to perform TMDB API operations
    """

    # load environment variable file and key
    load_dotenv()
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

    @staticmethod
    def get_streaming_providers(movie_id: int) -> Union[StreamingInfo, None]:
        """
        Returns streaming provider info for a given movie (US only), None if no results
        """

        def get_streamers_per_type(
            results: dict, streamer_type: str
        ) -> List[Tuple[str, str]]:
            retval = []
            if streamer_type not in results.keys():
                return retval

            for entry in results[streamer_type]:
                retval.append(
                    (
                        entry["provider_name"] + str(" - ") + streamer_type,
                        PosterPath.create_poster_link(entry["logo_path"]),
                    )
                )

            return retval

        response = TMDB.hit_api(f"movie/{movie_id}/watch/providers")

        if not response.ok:
            return None

        results: dict = TMDB.jsonify_response(response).get("results")

        # nothing in here!
        if len(results) == 0:
            print("No streaming results at all.")
            return None

        # US not present in streaming list
        if "US" not in results.keys():
            print("No US streaming information.")
            return None

        results: dict = results["US"]

        tmdb_link = ""
        if "link" in results:
            tmdb_link = results["link"]

        streamers = []
        streamers.extend(get_streamers_per_type(results, "flatrate"))
        streamers.extend(get_streamers_per_type(results, "rent"))
        streamers.extend(get_streamers_per_type(results, "buy"))

        return StreamingInfo(providers=streamers, tmdb_link=tmdb_link)

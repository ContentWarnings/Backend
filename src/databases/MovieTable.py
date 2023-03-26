from .ContentWarningTable import ContentWarningTable
from ..movies.MovieStub import MovieStub
from ..cw.ContentWarning import ContentWarning
import boto3
import os
from typing import List, Dict, Union


class MovieTable:
    DYNAMO_DB_CLIENT = boto3.client("dynamodb")
    MOVIES_TABLE = os.environ["MOVIES_TABLE"]

    @staticmethod
    def __parse_db_entry_to_MovieStub(item: dict) -> MovieStub:
        return MovieStub(
            id=item["id"]["N"],
            cmid=item["cmid"]["N"],
            cw=[entry["S"] for entry in item["cw"]["L"]],
        )

    @staticmethod
    def __itemize_MovieStub_to_db_entry(stub: MovieStub) -> dict:
        return {
            "id": {"N": str(stub.id)},
            "cmid": {"N": str(stub.cmid)},
            "cw": {"L": [{"S": w} for w in stub.cw]},
        }

    @staticmethod
    def get_all_ContentWarnings(id: int) -> List[Union[ContentWarning, None]]:
        """
        Return all ContentWarning objects from given movie/TMDB id
        """
        result = MovieTable.DYNAMO_DB_CLIENT.get_item(
            TableName=MovieTable.MOVIES_TABLE, Key={"id": {"N": str(id)}}
        )
        item = result.get("Item")

        if item is None:
            return list()

        stub = MovieTable.__parse_db_entry_to_MovieStub(item)
        return [ContentWarningTable.get_warning(cw_id) for cw_id in stub.cw]

    @staticmethod
    def delete_warning_from_movie(movie_id: int, cw_id: str) -> Dict[str, str]:
        """
        Deletes specified cw from movie's list
        """
        result = MovieTable.DYNAMO_DB_CLIENT.get_item(
            TableName=MovieTable.MOVIES_TABLE, Key={"id": {"N": str(movie_id)}}
        )
        item = result.get("Item")

        if item is None:
            return {"no movie of id": f"{movie_id}"}

        stub = MovieTable.__parse_db_entry_to_MovieStub(item)

        if cw_id not in stub.cw:
            return {f"cw {cw_id} not in movie": f"{movie_id}"}
        stub.cw.remove(cw_id)

        new_stub_item = MovieTable.__itemize_MovieStub_to_db_entry(stub)

        MovieTable.DYNAMO_DB_CLIENT.put_item(
            TableName=MovieTable.MOVIES_TABLE, Item=new_stub_item
        )

        return {f"deleted cw {cw_id} from movie": f"{movie_id}"}

    @staticmethod
    def add_warning_to_movie(id: int, cw_id: str) -> List[str]:
        """
        For given movie TMDB id (id), append new content warning id (cw_id) to database entry
        Returns list of content warnings UUIDs
        """
        result = MovieTable.DYNAMO_DB_CLIENT.get_item(
            TableName=MovieTable.MOVIES_TABLE, Key={"id": {"N": str(id)}}
        )
        item = result.get("Item")

        if item is None:
            new_stub_item = {
                "id": {"N": str(id)},
                "cmid": {"N": str(-1)},
                "cw": {"L": [{"S": cw_id}]},
            }

            MovieTable.DYNAMO_DB_CLIENT.put_item(
                TableName=MovieTable.MOVIES_TABLE, Item=new_stub_item
            )

            # return a list of the sole content warning id
            return [cw_id]

        else:
            stub = MovieTable.__parse_db_entry_to_MovieStub(item)

            # if CW is already present inside movie entry, return out
            if cw_id in stub.cw:
                return stub.cw

            stub.cw.append(cw_id)
            new_stub_item = MovieTable.__itemize_MovieStub_to_db_entry(stub)

            MovieTable.DYNAMO_DB_CLIENT.put_item(
                TableName=MovieTable.MOVIES_TABLE, Item=new_stub_item
            )

            return stub.cw

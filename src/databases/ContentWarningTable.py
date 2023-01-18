# References
# https://www.youtube.com/watch?v=mN39V5G3SXM
# https://stackoverflow.com/questions/56344868/invalid-type-for-parameter-error-when-using-put-item-dynamodb
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.delete_item
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/customizations/dynamodb.html#ref-valid-dynamodb-types

from ..cw.ContentWarning import ContentWarning
import boto3
import os
from typing import Dict, Union


class ContentWarningTable:
    DYNAMO_DB_CLIENT = boto3.client("dynamodb")
    CW_TABLE = os.environ["CW_TABLE"]

    @staticmethod
    def __itemize_ContentWarning_to_db_entry(cw: ContentWarning) -> dict:
        return {
            "name": {"S": cw.name},
            "id": {"S": cw.id},
            "movie_id": {"N": str(cw.movie_id)},
            "time": {"L": [{"S": str(entry)} for entry in cw.time]},
            "desc": {"S": cw.desc},
            "trust": {"N": str(cw.trust)},
            "upvotes": {"SS": list(cw.upvotes)},
            "downvotes": {"SS": list(cw.downvotes)},
        }

    @staticmethod
    def get_warning(id: str) -> Union[ContentWarning, None]:
        result = ContentWarningTable.DYNAMO_DB_CLIENT.get_item(
            TableName=ContentWarningTable.CW_TABLE, Key={"id": {"S": id}}
        )
        item = result.get("Item")

        if item is None:
            return item

        return ContentWarning(
            name=item["name"]["S"],
            id=item["id"]["S"],
            movie_id=item["movie_id"]["N"],
            time=[
                tuple(int(i) for i in entry["S"].strip("()").split(","))
                for entry in item["time"]["L"]
            ],
            desc=item["desc"]["S"],
            trust=item["trust"]["N"],
            upvotes=set(item["upvotes"]["SS"]),
            downvotes=set(item["downvotes"]["SS"]),
        )

    @staticmethod
    def add_warning(cw: ContentWarning) -> Union[ContentWarning, Dict[str, str]]:
        if ContentWarningTable.get_warning(cw.id) is not None:
            return {"error": f"CW with specified id {cw.id} already exists"}
        ContentWarningTable.DYNAMO_DB_CLIENT.put_item(
            TableName=ContentWarningTable.CW_TABLE,
            Item=ContentWarningTable.__itemize_ContentWarning_to_db_entry(cw),
        )
        return cw

    @staticmethod
    def edit_warning(cw: ContentWarning) -> Union[ContentWarning, Dict[str, str]]:
        content_warning = ContentWarningTable.get_warning(cw.id)

        # check that the ID backed by the cw exists first
        if content_warning is None:
            return {
                "error": f"CW with specified id {cw.id} does not exist. Cannot edit."
            }

        # if new warning changes link to movie, we should abort (our databases will get mixed up)
        if content_warning.movie_id != cw.movie_id:
            return {
                "error": f"Incoming CW {cw.id} is linked to a different movie ({cw.movie_id}), not current movie ({content_warning.movie_id}). Abort."
            }

        ContentWarningTable.DYNAMO_DB_CLIENT.put_item(
            TableName=ContentWarningTable.CW_TABLE,
            Item=ContentWarningTable.__itemize_ContentWarning_to_db_entry(cw),
        )
        return cw

    @staticmethod
    def delete_warning(cw_id: str) -> Dict[str, str]:
        result = ContentWarningTable.DYNAMO_DB_CLIENT.delete_item(
            TableName=ContentWarningTable.CW_TABLE,
            Key={
                "id": {"S": cw_id},
            },
        )

        message = (
            "deleted"
            if result["ResponseMetadata"]["HTTPStatusCode"] == 200
            else "failed to delete"
        )
        return {message: cw_id}

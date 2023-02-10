# References
# https://www.youtube.com/watch?v=mN39V5G3SXM
# https://stackoverflow.com/questions/56344868/invalid-type-for-parameter-error-when-using-put-item-dynamodb
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.delete_item
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/customizations/dynamodb.html#ref-valid-dynamodb-types

from fastapi import status
from ..cw.ContentWarning import ContentWarning
from ..cw.ContentWarningNames import ContentWarningNames
from ..users.User import User
import boto3
import os
from typing import Dict, Tuple, Union
from fastapi import HTTPException, status


class ContentWarningTable:
    DYNAMO_DB_CLIENT = boto3.client("dynamodb")
    CW_TABLE = os.environ["CW_TABLE"]

    @staticmethod
    def __itemize_ContentWarning_to_db_entry(cw: ContentWarning) -> dict:
        return {
            "name": {"S": cw.name.value},
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
            name=ContentWarningNames(item["name"]["S"]),
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
    def add_warning(cw: ContentWarning) -> Union[ContentWarning, Tuple[int, str]]:
        """
        Attempts to add specified content warning to table.
        If fails, returns tuple of HTTP status error and detail
        """
        if ContentWarningTable.get_warning(cw.id) is not None:
            return (
                status.HTTP_409_CONFLICT,
                f"CW with specified id {cw.id} already exists",
            )
        ContentWarningTable.DYNAMO_DB_CLIENT.put_item(
            TableName=ContentWarningTable.CW_TABLE,
            Item=ContentWarningTable.__itemize_ContentWarning_to_db_entry(cw),
        )
        return cw

    @staticmethod
    def edit_warning(cw: ContentWarning) -> Union[ContentWarning, Tuple[int, str]]:
        """
        Attempts to edit specified content warning.
        If fails, returns tuple of HTTP status error and detail
        """
        content_warning = ContentWarningTable.get_warning(cw.id)

        # check that the ID backed by the cw exists first
        if content_warning is None:
            return (
                status.HTTP_404_NOT_FOUND,
                f"CW with specified id {cw.id} does not exist. Cannot edit.",
            )

        # if new warning changes link to movie, we should abort (our databases will get mixed up)
        if content_warning.movie_id != cw.movie_id:
            print(
                f"Incoming CW {cw.id} is linked to a different movie ({cw.movie_id}), not current movie ({content_warning.movie_id}). Abort."
            )
            return (status.HTTP_409_CONFLICT, "Clashing incoming/existing movie ids")

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

    @staticmethod
    def ensure_user_can_edit_cw(user: User, cw: ContentWarning) -> None:
        """
        Verifies whether user can edit specified CW (whether they own it), if not, raise exception
        """
        if cw.id not in user.contributions:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User must own CW to edit it.",
            )

    @staticmethod
    def __voting_op(cw_id: str, hashed_ip_address: str, is_upvote: bool):
        cw = ContentWarningTable.get_warning(cw_id)
        if cw is None:
            return (status.HTTP_404_NOT_FOUND, f"CW {cw_id} does not exist.")

        set_to_add = cw.upvotes if is_upvote else cw.downvotes
        other_set = cw.downvotes if is_upvote else cw.upvotes
        desc = "upvote" if is_upvote else "downvote"

        if hashed_ip_address in set_to_add:
            return (status.HTTP_405_METHOD_NOT_ALLOWED, f"Cannot {desc} again.")

        # if same IP has voted for opposing operation, this is OK; we remove IP address and will add
        # IP address to designated set instead
        if hashed_ip_address in other_set:
            other_set.remove(hashed_ip_address)

        set_to_add.add(hashed_ip_address)
        cw.calculate_trust_score()

        ContentWarningTable.DYNAMO_DB_CLIENT.put_item(
            TableName=ContentWarningTable.CW_TABLE,
            Item=ContentWarningTable.__itemize_ContentWarning_to_db_entry(cw),
        )

        return "Success"

    @staticmethod
    def upvote(cw_id: str, hashed_ip_address: str) -> Union[str, Tuple[int, str]]:
        """
        Attempts to upvote; returns success string or tuple of HTTP status code and error string
        """
        return ContentWarningTable.__voting_op(cw_id, hashed_ip_address, True)

    @staticmethod
    def downvote(cw_id: str, hashed_ip_address: str) -> Union[str, Tuple[int, str]]:
        """
        Attempts to downvote; returns success string or tuple of HTTP status code and error string
        """
        return ContentWarningTable.__voting_op(cw_id, hashed_ip_address, False)

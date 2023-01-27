from ..users.UserVerification import UserVerification
import boto3
from fastapi import status
import os
from typing import Tuple, Union


class UserVerificationTable:
    """
    Simple mapping of user email addresses to UUIDs of their verification code
    """

    DYNAMO_DB_CLIENT = boto3.client("dynamodb")
    USER_VERIFICATION_TABLE = os.environ["USER_VERIFICATION_TABLE"]

    @staticmethod
    def __parse_db_entry_to_UserVerification(item: dict) -> UserVerification:
        return UserVerification(email=item["email"]["S"], code=item["code"]["S"])

    @staticmethod
    def __itemize_UserVerification_to_db_entry(uv_obj: UserVerification) -> dict:
        return {"email": {"S": uv_obj.email}, "code": {"S": uv_obj.code}}

    @staticmethod
    def get_user_verification_obj(email: str) -> Union[UserVerification, None]:
        item = UserVerificationTable.DYNAMO_DB_CLIENT.get_item(
            TableName=UserVerificationTable.USER_VERIFICATION_TABLE,
            Key={"email": {"S": email}},
        ).get("Item")

        if item is None:
            return item

        return UserVerificationTable.__parse_db_entry_to_UserVerification(item)

    @staticmethod
    def add_user(email: str, verif_code: str) -> Union[None, Tuple[int, str]]:
        """
        Adds user information to verification table
        If fails, returns tuple of HTTP status code and error message
        """
        item = UserVerificationTable.get_user_verification_obj(email)

        if item is not None:
            return (
                status.HTTP_409_CONFLICT,
                f"User with specified email {email} already exists.",
            )

        uv_obj = UserVerification(email=email, code=verif_code)

        UserVerificationTable.DYNAMO_DB_CLIENT.put_item(
            TableName=UserVerificationTable.USER_VERIFICATION_TABLE,
            Item=UserVerificationTable.__itemize_UserVerification_to_db_entry(uv_obj),
        )

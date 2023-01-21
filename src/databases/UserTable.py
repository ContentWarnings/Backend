from ..security.Bcrypter import Bcrypter
from ..users.User import User, UserReduced
import boto3
from fastapi import status
import os
from typing import Tuple, Union


class UserTable:
    """
    Holds all of our User objects data
    """

    DYNAMO_DB_CLIENT = boto3.client("dynamodb")
    USER_TABLE = os.environ["USER_TABLE"]

    @staticmethod
    def __parse_db_entry_to_User(item: dict) -> User:
        return User(
            email=item["email"]["S"],
            password=item["password"]["S"],
            verified=item["verified"]["BOOL"],
            contributions=[entry["S"] for entry in item["contributions"]["L"]],
        )

    @staticmethod
    def __itemize_User_to_db_entry(user: User) -> dict:
        return {
            "email": {"S": user.email},
            "password": {"S": user.password},
            "verified": {"BOOL": user.verified},
            "contributions": {"L": [{"S": cw_id} for cw_id in user.contributions]},
        }

    @staticmethod
    def get_user(email: str) -> Union[None, User]:
        item = UserTable.DYNAMO_DB_CLIENT.get_item(
            TableName=UserTable.USER_TABLE,
            Key={"email": {"S": email}},
        ).get("Item")

        if item is None:
            return None

        return UserTable.__parse_db_entry_to_User(item)

    @staticmethod
    def add_user(user_reduced: UserReduced) -> Union[None, Tuple[int, str]]:
        """
        Adds user to table
        If fails, returns tuple of HTTP status code and error message
        """
        item = UserTable.get_user(user_reduced.email)

        if item is not None:
            return (
                status.HTTP_409_CONFLICT,
                f"User with specified email {user_reduced.email} already exists.",
            )

        # encrypt user passwords before placing inside db
        user_reduced.password = Bcrypter.encrypt_password(user_reduced.password)

        UserTable.DYNAMO_DB_CLIENT.put_item(
            TableName=UserTable.USER_TABLE,
            Item=UserTable.__itemize_User_to_db_entry(user_reduced.to_User()),
        )

    @staticmethod
    def set_user_to_verified(email: str):
        """
        Sets User's verified field to true
        """
        user = UserTable.get_user(email)
        user.verified = True

        UserTable.DYNAMO_DB_CLIENT.put_item(
            TableName=UserTable.USER_TABLE,
            Item=UserTable.__itemize_User_to_db_entry(user),
        )

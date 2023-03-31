import boto3
import os
from ..users.LowTrustUser import LowTrustUser
from typing import Union


class LowTrustUserTable:
    """
    Holds objects containing information on users with low trust
    """

    DYNAMO_DB_CLIENT = boto3.client("dynamodb")
    LOW_TRUST_USER_TABLE = os.environ["LOW_TRUST_USER_TABLE"]

    @staticmethod
    def __parse_db_entry_to_LowTrustUser(item: dict) -> LowTrustUser:
        return LowTrustUser(
            email=item["email"]["S"],
            num_good_contributions=item["num_good_contributions"]["N"],
            num_deleted_contributions=item["num_deleted_contributions"]["N"],
            is_low_trust=item["is_low_trust"]["BOOL"],
        )

    @staticmethod
    def __itemize_LowTrustUser_to_db_entry(ltu_obj: LowTrustUser) -> dict:
        return {
            "email": {"S": ltu_obj.email},
            "num_good_contributions": {"N": str(ltu_obj.num_good_contributions)},
            "num_deleted_contributions": {"N": str(ltu_obj.num_deleted_contributions)},
            "is_low_trust": {"BOOL": ltu_obj.is_low_trust},
        }

    @staticmethod
    def get(email: str) -> Union[LowTrustUser, None]:
        """
        Returns LTU object if exists, else None
        """

        item = LowTrustUserTable.DYNAMO_DB_CLIENT.get_item(
            TableName=LowTrustUserTable.LOW_TRUST_USER_TABLE,
            Key={"email": {"S": email}},
        ).get("Item")

        if item is None:
            return None

        return LowTrustUserTable.__parse_db_entry_to_LowTrustUser(item)

    @staticmethod
    def delete(email: str):
        """
        Deletes a LTU object
        """
        try:
            LowTrustUserTable.DYNAMO_DB_CLIENT.delete_item(
                TableName=LowTrustUserTable.LOW_TRUST_USER_TABLE,
                Key={
                    "email": {"S": email},
                },
            )
        except Exception as ex:
            print(f"Error deleting LTU obj {email}: {ex}")

    @staticmethod
    def add_or_edit(ltu_obj: LowTrustUser):
        """
        Adds to table or edits given LTU object
        """
        LowTrustUserTable.DYNAMO_DB_CLIENT.put_item(
            TableName=LowTrustUserTable.LOW_TRUST_USER_TABLE,
            Item=LowTrustUserTable.__itemize_LowTrustUser_to_db_entry(ltu_obj),
        )

    @staticmethod
    def change_email(old_email: str, new_email: str):
        """
        Changes email of an existing LTU obj (if exists)
        """

        existing_ltu_obj = LowTrustUserTable.get(old_email)
        if existing_ltu_obj is None:
            print(
                f"Invalid 'existing' email {old_email} passed into change_email() LTU."
            )
            return

        LowTrustUserTable.delete(old_email)

        existing_ltu_obj.email = new_email
        LowTrustUserTable.DYNAMO_DB_CLIENT.put_item(
            TableName=LowTrustUserTable.LOW_TRUST_USER_TABLE,
            Item=LowTrustUserTable.__itemize_LowTrustUser_to_db_entry(existing_ltu_obj),
        )

from .LowTrustUserTable import LowTrustUserTable
from .ContentWarningTable import ContentWarningTable
from ..security.Bcrypter import Bcrypter
from ..users.User import User, UserReduced
from ..users.LowTrustUser import LowTrustUser
import boto3
from fastapi import HTTPException, status
import os
from typing import Dict, Tuple, Union


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
            new_pending_email=item["new_pending_email"]["S"],
            password=item["password"]["S"],
            verified=item["verified"]["BOOL"],
            contributions=[entry["S"] for entry in item["contributions"]["L"]],
        )

    @staticmethod
    def __itemize_User_to_db_entry(user: User) -> dict:
        return {
            "email": {"S": user.email},
            "new_pending_email": {"S": user.new_pending_email},
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

        # hash user passwords before placing inside db
        user_reduced.password = Bcrypter.hash_password(user_reduced.password)

        UserTable.DYNAMO_DB_CLIENT.put_item(
            TableName=UserTable.USER_TABLE,
            Item=UserTable.__itemize_User_to_db_entry(user_reduced.to_User()),
        )

    @staticmethod
    def add_user_obj(user: User) -> None:
        """
        Adds user object to table, hashing password, too
        """
        user.password = Bcrypter.hash_password(user.password)

        UserTable.DYNAMO_DB_CLIENT.put_item(
            TableName=UserTable.USER_TABLE,
            Item=UserTable.__itemize_User_to_db_entry(user),
        )

    @staticmethod
    def delete_user(email: str) -> str:
        """
        Deletes user, returning msg of success or failure
        """
        # perform a check if user even exists first
        UserTable.get_user_from_decoded_jwt(email)

        result = UserTable.DYNAMO_DB_CLIENT.delete_item(
            TableName=UserTable.USER_TABLE,
            Key={
                "email": {"S": email},
            },
        )

        return (
            f"Successfully deleted user {email}"
            if result["ResponseMetadata"]["HTTPStatusCode"] == status.HTTP_200_OK
            else f"Failed to delete user {email}"
        )

    @staticmethod
    def set_user_to_verified(email: str, is_verified: bool = True):
        """
        Sets User's verified field to true
        """
        user = UserTable.get_user(email)
        user.verified = is_verified

        UserTable.DYNAMO_DB_CLIENT.put_item(
            TableName=UserTable.USER_TABLE,
            Item=UserTable.__itemize_User_to_db_entry(user),
        )

    @staticmethod
    def edit_user(user: User):
        """
        Edits existing user inside table
        """
        UserTable.DYNAMO_DB_CLIENT.put_item(
            TableName=UserTable.USER_TABLE,
            Item=UserTable.__itemize_User_to_db_entry(user),
        )

    @staticmethod
    def prune_downvoted_cws_and_update_low_trust(
        user_email: str,
    ) -> Union[LowTrustUser, None]:
        """
        Prunes CWs that point to nowhere in CW table; returns LowTrustUser object if exists, else None
        Also updates LowTrustUser table if required. Why? Pruning CWs occurs when other users downvote
        this user's CWs enough to warrant removal. If there are enough CW IDs/pointers that
        are "null", this user's low trust status updates.
        """
        user = UserTable.get_user(user_email)
        if user is None:
            return None

        new_cw_list = [
            cw_id
            for cw_id in user.contributions
            if ContentWarningTable.get_warning(cw_id) is not None
        ]

        # case 1: if there are no downvoted to deletion CWs
        if len(new_cw_list) == len(user.contributions):
            return LowTrustUserTable.get(user_email)

        # case 2: CW IDs exist which are effectively null pointers
        # (CWs that other users have downvoted to deletion)
        num_bad_contributions = abs(len(user.contributions) - len(new_cw_list))
        num_good_contributions = len(new_cw_list)

        user.contributions = new_cw_list
        UserTable.DYNAMO_DB_CLIENT.put_item(
            TableName=UserTable.USER_TABLE,
            Item=UserTable.__itemize_User_to_db_entry(user),
        )

        low_trust_user_obj: LowTrustUser = LowTrustUserTable.get(user_email)

        # if user doesn't have a LTU object, make one
        if low_trust_user_obj is None:
            low_trust_user_obj = LowTrustUser(
                email=user_email,
                num_good_contributions=num_good_contributions,
                num_deleted_contributions=num_bad_contributions,
                is_low_trust=False,
            )
        # otherwise, update fields of existing LTU object
        else:
            low_trust_user_obj.num_good_contributions = num_good_contributions
            low_trust_user_obj.num_deleted_contributions += num_bad_contributions

        # if user's not already low trust, determine if they _should be_ low trust
        if not low_trust_user_obj.is_low_trust:
            low_trust_user_obj.is_low_trust = LowTrustUser.is_user_low_trust(
                low_trust_user_obj.num_good_contributions,
                low_trust_user_obj.num_deleted_contributions,
            )

        # write LTU object back to database
        LowTrustUserTable.add_or_edit(low_trust_user_obj)

        return low_trust_user_obj

    @staticmethod
    def delete_cw(user_email: str, cw_id: str) -> Dict[str, str]:
        """
        Deletes specified CW from user
        """
        user = UserTable.get_user(user_email)
        if user is None:
            return {"no user with email": user_email}

        if cw_id in user.contributions:
            user.contributions.remove(cw_id)
        else:
            return {f"user {user_email} does not have contribution with id": cw_id}

        UserTable.DYNAMO_DB_CLIENT.put_item(
            TableName=UserTable.USER_TABLE,
            Item=UserTable.__itemize_User_to_db_entry(user),
        )

        return {f"deleted cw {cw_id} from user": user_email}

    @staticmethod
    def get_user_from_decoded_jwt(decoded_email: str) -> User:
        """
        Retrieves user from decoded email, with enhanced error checking (returns HTTP exceptions
        if errors happen)
        """
        if decoded_email is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User does not exist or password does not match.",
            )

        user = UserTable.get_user(decoded_email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User does not exist or password does not match.",
            )

        return user

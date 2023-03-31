from pydantic import BaseModel


class LowTrustUser(BaseModel):
    """
    Objects stored in LowTrustUser (LTU) database. A user becomes low trust when enough
    of their CW posts are downvoted to deletion by other users. Henceforth, their posts
    are no longer persisted to backend/viewable.
    """

    email: str

    # total number of good CWs user has posted (not deleted by others' downvotes)
    num_good_contributions: int

    # total number of CWs posted by user, downvoted enough times to warrant deletion
    num_deleted_contributions: int

    # 'True' means their future CW additions are no longer posted to database
    is_low_trust: bool

    @staticmethod
    def __get_num_contributions_threshold_for_low_trust_user() -> int:
        """
        Returns minimum # net contributions needed to be considered low trust
        """
        return 10

    @staticmethod
    def __get_ratio_of_bad_posts_threshold_for_low_trust_user() -> float:
        """
        Returns ratio of (bad posts : total posts) for which a user is considered low trust
        """
        return 0.3

    @staticmethod
    def is_user_low_trust(
        num_good_contributions: int, num_deleted_contributions: int
    ) -> bool:
        """
        Given number of total contributions and number of total deleted contributions, determines
        whether a given user is low trust
        """
        total_contributions = num_good_contributions + num_deleted_contributions
        bad_post_ratio = num_deleted_contributions / total_contributions
        return (
            total_contributions
            >= LowTrustUser.__get_num_contributions_threshold_for_low_trust_user()
            and bad_post_ratio
            >= LowTrustUser.__get_ratio_of_bad_posts_threshold_for_low_trust_user()
        )

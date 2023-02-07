import uuid


class CodeGenerator:
    @staticmethod
    def create_new_verification_code() -> str:
        """
        Generates a new string UUID verification code
        """
        return str(uuid.uuid4())

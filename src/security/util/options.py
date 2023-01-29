from dotenv import load_dotenv
import os


class Options:
    # load environment variable file and key
    load_dotenv()

    __JWT_SECRET = os.environ["JWT_SECRET"]
    __JWT_ALGORITHM = os.environ["JWT_ALGORITHM"]
    __JWT_SUDO_LIFETIME = os.environ["JWT_SUDO_LIFETIME"]
    __JWT_USER_LIFETIME = os.environ["JWT_USER_LIFETIME"]

    @staticmethod
    def get_secret():
        return Options.__JWT_SECRET

    @staticmethod
    def get_algorithm():
        return Options.__JWT_ALGORITHM

    @staticmethod
    def get_sudo_lifetime():
        return int(Options.__JWT_SUDO_LIFETIME)

    @staticmethod
    def get_user_lifetime():
        return int(Options.__JWT_USER_LIFETIME)

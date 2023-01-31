# References
# https://www.geeksforgeeks.org/python-convert-string-to-bytes/
# https://docs.python.org/3/library/hashlib.html

import hashlib


class Sha256:
    """
    SHA256 hashing helper
    """

    @staticmethod
    def hash(s: str) -> str:
        hasher = hashlib.sha256()
        hasher.update(bytes(s, "UTF-8"))
        return hasher.hexdigest()

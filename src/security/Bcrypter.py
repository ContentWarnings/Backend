# References
#
# These references were for the nodeJS lambda created for the password encryption
# https://stackoverflow.com/questions/71981894/referenceerror-require-is-not-defined-in-es-module-scope-you-can-use-import-in
# https://github.com/dcodeIO/bcrypt.js
# https://stackoverflow.com/questions/73474948/aws-lambda-sftp-task-timed-out-after-3-01-seconds
# https://www.youtube.com/watch?v=RnFowJ130pc
# https://www.youtube.com/watch?v=RfbUOglbuLc
# https://www.youtube.com/watch?v=5QwrseYLwNM
# https://stackoverflow.com/questions/37498124/accessdeniedexception-user-is-not-authorized-to-perform-lambdainvokefunction

import boto3
import json


class Bcrypter:
    """
    Hits a nodeJS lambda calling bcryptJS to perform password encryption.
    We tried to perform encryption natively in Python via bcrypt module, but compiling on our
    host OS was different than Amazon's Linux servers, which turned into a mess.
    This is a helpful workaround.
    """

    LAMBDA_FUNCTION_NAME = "bcrypt_password"
    LAMBDA_REGION = "us-east-1"
    INVOKE_LAMBDA = boto3.client("lambda", region_name=LAMBDA_REGION)

    @staticmethod
    def __invoke_security_lambda(
        hash: bool, password: str, hashedPassword: str = ""
    ) -> bytes:
        response = Bcrypter.INVOKE_LAMBDA.invoke(
            FunctionName=Bcrypter.LAMBDA_FUNCTION_NAME,
            InvocationType="RequestResponse",
            Payload=json.dumps(
                {"hash": hash, "password": password, "hashedPassword": hashedPassword}
            ),
        )

        return response["Payload"].read()

    @staticmethod
    def hash_password(password: str) -> str:
        return str(
            Bcrypter.__invoke_security_lambda(hash=True, password=password),
            encoding="utf-8",
        ).strip('"')

    @staticmethod
    def do_passwords_match(password: str, encrypted_password: str) -> bool:
        bool_msg = str(
            Bcrypter.__invoke_security_lambda(
                hash=False, password=password, hashedPassword=encrypted_password
            ),
            encoding="utf-8",
        ).capitalize()

        return True if bool_msg == "True" else False

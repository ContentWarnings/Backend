# References
# https://stackabuse.com/validate-email-addresses-in-python-with-email-validator/
# https://github.com/JoshData/python-email-validator
# https://docs.sendgrid.com/for-developers/sending-email/quickstart-python
# https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
# https://github.com/sendgrid/sendgrid-python/blob/main/use_cases/send_a_single_email_to_a_single_recipient.md

from dotenv import load_dotenv
from email_validator import validate_email, EmailNotValidError
from enum import Enum
from fastapi import HTTPException, status
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


class Emailer:
    """
    Bundles email related operations
    """

    # load .env and key
    load_dotenv()
    __SENDGRID_API_KEY = os.environ["SENDGRID_API_KEY"]
    __SENDER_EMAIL = "no-reply@moviementor.app"

    class VerificationCode(Enum):
        """
        Different types of verification codes sent to users via email
        """

        VERIFICATION = "Verification"
        DELETION = "Deletion"
        PASSWORD_RESET = "Password Reset"

    @staticmethod
    def perform_email_validation(email: str) -> None:
        """
        Validates given email, raising errors if invalid
        """
        try:
            # call module's function here to outsource work
            validate_email(email)
        except EmailNotValidError as ex:
            # logging
            print(f"Error validating email {email}")
            print(ex)

            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail=f"Email {email} is invalid.",
            )

    @staticmethod
    def __send_email(receiver_email: str, subject: str, msg: str) -> bool:
        Emailer.perform_email_validation(receiver_email)

        print(f"Sending email of {msg} to {receiver_email}")  # logging

        message = Mail(
            from_email=Emailer.__SENDER_EMAIL,
            to_emails=receiver_email,
            subject=subject,
            html_content=f"<h3>{msg}</h3>",
        )
        try:
            sg = SendGridAPIClient(Emailer.__SENDGRID_API_KEY)
            sg.send(message)
            return True
        except Exception as ex:
            print("Error sending email:")
            print(ex)
            return False

    @staticmethod
    def send_code_via_email(
        receiver_email: str, code: str, code_type: VerificationCode
    ) -> bool:
        """
        Sends a verification code of specified type to specified email
        """

        subject = f"MovieMentor {code_type.value} Code"
        message = (
            f"Thank you for using MovieMentor! Your {code_type.value} code is {code}."
        )
        return Emailer.__send_email(receiver_email, subject, message)

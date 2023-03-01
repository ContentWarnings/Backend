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
    def generate_html(subject: str, body: str, link: str):
        return f"""
<!DOCTYPE html>
<html>
<head>
    <style type="text/css">
        * {{
            box-sizing: border-box;
            transition: background-color 100ms cubic-bezier(0.4, 0, 0.2, 1);
        }}
        html, body, .bkgd {{
            background-color: #1e1e1e;
            background: #1e1e1e;
            color: white;
            margin: 0;
            font-family: "Roboto", sans-serif;
        }}
        .nav {{
            width: 100%;
            text-align: center;
            background-color: #7e57c2;
            background: #7e57c2;
            padding: 10px;
            height: 70px;
        }}
        .main {{
            max-width: 500px;
            width: 100%;
            margin: auto;
            padding: 10px;
        }}
        p {{
            font-size: 18px;
            margin: 0;
            margin-bottom: 5px;
            color: #ffffff;
        }}
        a {{
            background-color: #7e57c2;
            background: #7e57c2;
            padding: 7px 14px;
            border-radius: 5px;
            font-weight: bold;
            font-size: 21px;
            margin: 10px 0;
            color: #ffffff!important;
            display: inline-block;
            text-decoration: none;
        }}
        a:hover {{
            background-color: #b085f5;
            background: #b085f5;
        }}
        img {{
            color: white;
            font-weight: bold;
            font-size: 42px;
            color: #ffffff;
            height: 50px;
            display: inline-block;
            width: fit-content;
            border: none;
        }}
    </style>
</head>
<body class="bkgd">
    <div class="nav">
        <img alt="MovieMentor" src="https://moviementor.app/logotext.png"></img>
    </div>
    <div class="main">
        <h1>{subject}</h1>
        <p>{body}</p>
        <a style="color: #ffffff" color="white" href="{link}">Verify</a>
    </div>
</body>
</html>
        """

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
            print(f"Error validating email!")
            print(ex)

            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail=f"Email address is invalid.",
            )

    @staticmethod
    def __send_email(receiver_email: str, subject: str, msg: str) -> bool:
        Emailer.perform_email_validation(receiver_email)

        print(f"Email dispatch!")  # logging

        message = Mail(
            from_email=Emailer.__SENDER_EMAIL,
            to_emails=receiver_email,
            subject=subject,
            html_content=msg,
        )
        try:
            sg = SendGridAPIClient(Emailer.__SENDGRID_API_KEY)
            sg.send(message)
            return True
        except Exception as ex:
            print("Error sending email:")
            print(ex)

            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail=f"Error sending email to {receiver_email}.",
            )

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
        link = f"https://moviementor.app/account/verify?src={code_type.value.lower().replace(' ', '_')}&token={code}"

        if code_type == Emailer.VerificationCode.VERIFICATION:
            message = "Thank you for signing up as a contributor on MovieMentor! To finish setting up your account, click the Verify button below. If this was not done by you, you can safely ignore this email."
            link = f"https://moviementor.app/account/verify?src=register&token={code}&email={receiver_email}"
        elif code_type == Emailer.VerificationCode.DELETION:
            message = "It's sad to see you go! To finish deleting your account, click the Verify button below while logged into your MovieMentor account."
            link = f"https://moviementor.app/account/verify?src=delete&token={code}"
        elif code_type == Emailer.VerificationCode.PASSWORD_RESET:
            message = "We heard you forgot your password! To finish deleting your account, click the Verify button below. If this was not done by you, you can safely ignore this email."
            link = f"https://moviementor.app/account/verify/passwd?email={receiver_email}&token={code}"

        html = Emailer.generate_html(subject, message, link)

        return Emailer.__send_email(receiver_email, subject, html)

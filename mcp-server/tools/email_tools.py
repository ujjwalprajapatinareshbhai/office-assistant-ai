import smtplib
import os
import time

from email.message import EmailMessage
from dotenv import load_dotenv


load_dotenv()


EMAIL_ADDRESS = os.getenv(
    "EMAIL_ADDRESS"
)

EMAIL_PASSWORD = os.getenv(
    "EMAIL_PASSWORD"
)


# =========================================================
# EMAIL CONFIGURATION
# =========================================================

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

# Number of attempts for temporary SMTP failures
MAX_RETRIES = 3

# Seconds to wait between retries
RETRY_DELAY = 5


# =========================================================
# SEND EMAIL
# =========================================================

def send_email(
    to: str,
    subject: str,
    body: str
):
    """
    Send an email using Gmail SMTP.

    Temporary SMTP errors such as Gmail 451 responses
    are retried automatically.
    """

    if not EMAIL_ADDRESS:

        return (
            "Failed to send email: "
            "EMAIL_ADDRESS is not configured."
        )

    if not EMAIL_PASSWORD:

        return (
            "Failed to send email: "
            "EMAIL_PASSWORD is not configured."
        )

    if not to:

        return (
            "Failed to send email: "
            "Recipient email address is missing."
        )

    print(
        "\n📧 Sending email..."
    )

    print(
        f"From: {EMAIL_ADDRESS}"
    )

    print(
        f"To: {to}"
    )

    print(
        f"Subject: {subject}"
    )

    print(
        f"Body:\n{body}"
    )

    # =====================================================
    # CREATE EMAIL MESSAGE ONCE
    # =====================================================

    msg = EmailMessage()

    msg["From"] = EMAIL_ADDRESS

    msg["To"] = to

    msg["Subject"] = subject

    msg.set_content(
        body
    )

    # =====================================================
    # RETRY LOOP
    # =====================================================

    for attempt in range(
        1,
        MAX_RETRIES + 1
    ):

        server = None

        try:

            print(
                f"\n📨 Email attempt "
                f"{attempt}/{MAX_RETRIES}"
            )

            # -------------------------------------------------
            # CONNECT TO GMAIL
            # -------------------------------------------------

            server = smtplib.SMTP(
                SMTP_HOST,
                SMTP_PORT,
                timeout=30
            )

            server.ehlo()

            server.starttls()

            server.ehlo()

            print(
                "🔐 Logging into Gmail SMTP..."
            )

            # -------------------------------------------------
            # LOGIN
            # -------------------------------------------------

            server.login(
                EMAIL_ADDRESS,
                EMAIL_PASSWORD
            )

            print(
                "✅ Gmail SMTP login successful."
            )

            # -------------------------------------------------
            # SEND
            # -------------------------------------------------

            print(
                "📨 Sending message..."
            )

            result = server.send_message(
                msg
            )

            print(
                f"📬 SMTP result: {result}"
            )

            # -------------------------------------------------
            # SUCCESS
            # -------------------------------------------------

            print(
                "\n✅ EMAIL SENT SUCCESSFULLY"
            )

            return (
                f"Email sent successfully to "
                f"{to} with subject "
                f"'{subject}'."
            )

        # =====================================================
        # AUTHENTICATION ERROR
        # =====================================================

        except smtplib.SMTPAuthenticationError as e:

            print(
                f"\n❌ Gmail authentication failed: {e}"
            )

            return (
                "Failed to send email: Gmail SMTP "
                "authentication failed. Check "
                "EMAIL_ADDRESS and "
                "EMAIL_PASSWORD/App Password."
            )

        # =====================================================
        # SMTP ERROR
        # =====================================================

        except smtplib.SMTPResponseException as e:

            error_code = e.smtp_code

            error_message = e.smtp_error

            print(
                f"\n❌ SMTP response error:"
            )

            print(
                f"Code: {error_code}"
            )

            print(
                f"Message: {error_message}"
            )

            # -------------------------------------------------
            # TEMPORARY GMAIL ERROR
            #
            # 4xx SMTP codes are normally temporary.
            #
            # Example:
            #
            # 451 4.3.0 Mail server temporarily
            # rejected message
            # -------------------------------------------------

            if (
                400
                <= error_code
                < 500
            ):

                if attempt < MAX_RETRIES:

                    print(
                        "\n⏳ Gmail temporarily "
                        "rejected the message."
                    )

                    print(
                        f"🔄 Retrying in "
                        f"{RETRY_DELAY} seconds..."
                    )

                    time.sleep(
                        RETRY_DELAY
                    )

                    continue

                # -------------------------------------------------
                # ALL RETRIES FAILED
                # -------------------------------------------------

                print(
                    "\n❌ EMAIL FAILED AFTER "
                    f"{MAX_RETRIES} ATTEMPTS"
                )

                return (
                    "Failed to send email: Gmail "
                    "temporarily rejected the message "
                    f"after {MAX_RETRIES} attempts. "
                    f"SMTP {error_code}: "
                    f"{error_message}"
                )

            # -------------------------------------------------
            # PERMANENT SMTP ERROR
            # -------------------------------------------------

            print(
                "\n❌ Permanent SMTP error."
            )

            return (
                "Failed to send email: "
                f"SMTP {error_code}: "
                f"{error_message}"
            )

        # =====================================================
        # GENERAL SMTP EXCEPTION
        # =====================================================

        except smtplib.SMTPException as e:

            print(
                f"\n❌ SMTP error: {e}"
            )

            # Some SMTP errors don't expose a numeric code.
            # Retry them because the connection may have
            # failed temporarily.

            if attempt < MAX_RETRIES:

                print(
                    "\n⏳ Temporary SMTP problem."
                )

                print(
                    f"🔄 Retrying in "
                    f"{RETRY_DELAY} seconds..."
                )

                time.sleep(
                    RETRY_DELAY
                )

                continue

            return (
                "Failed to send email: "
                f"SMTP error: {e}"
            )

        # =====================================================
        # OTHER ERROR
        # =====================================================

        except Exception as e:

            print(
                f"\n❌ Email error: {e}"
            )

            return (
                f"Failed to send email: {e}"
            )

        # =====================================================
        # CLOSE SMTP CONNECTION
        # =====================================================

        finally:

            if server is not None:

                try:

                    server.quit()

                except Exception:

                    pass

    # =========================================================
    # SAFETY FALLBACK
    # =========================================================

    return (
        "Failed to send email after "
        f"{MAX_RETRIES} attempts."
    )

import os

from flask import session

ALLOWED_EMAILS = {
    email.strip().lower()
    for email in os.environ.get("ALLOWED_EMAILS", "").split(",")
    if email.strip()
}


def current_email():
    email = session.get("email")
    if email and email in ALLOWED_EMAILS:
        return email
    session.pop("email", None)
    return None

"""Herrfors API."""

from requests import Session

from .exception import CreateSessionError

HTTP_REDIRECT = 302

def create_session(usage_place: int, customer_number: int) -> Session:
    """Create a Herrfors API session."""
    session = Session()

    login_payload = {
        "usageplace": usage_place,
        "customernumber": customer_number,
    }

    login_result = session.post("https://meter.katterno.fi/index.php",
                                data=login_payload,
                                allow_redirects=False)

    if login_result.status_code != HTTP_REDIRECT:
        raise CreateSessionError

    return session

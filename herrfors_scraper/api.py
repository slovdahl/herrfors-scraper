"""Herrfors API."""

from datetime import date

from requests import Session

from herrfors_scraper.const import Type
from herrfors_scraper.exception import (
    CreateSessionError,
    NoDataError,
    TooLittleDataReceivedError,
    UnknownTypeError,
)

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

def get_data(session: Session, start: date, end: date, scrape_type: Type) -> list:
    """Get data for the given range and of the given type."""
    if scrape_type == Type.PRODUCTION:
        export_type = "production"
    elif scrape_type == Type.CONSUMPTION:
        export_type = "hours"
    else:
        raise UnknownTypeError

    export_payload = {
        "exporttype": export_type,
        "export-range": f"{start.strftime('%d.%m.%Y')} - {end.strftime('%d.%m.%Y')}",
    }

    result = session.post("https://meter.katterno.fi/export.php",
                          data=export_payload,
                          allow_redirects=False)

    if result.status_code != 200:
        raise NoDataError

    if (
        "Content-Disposition" not in result.headers and
        "content-disposition" not in result.headers
    ):
        raise NoDataError

    non_empty_lines = [line.strip() for line in result.text.split("\n") if line.strip() != ""]
    non_empty_lines = [line for line in non_empty_lines if not line.startswith("Tid")]

    if len(non_empty_lines) == 0:
        raise NoDataError

    if len(non_empty_lines) <= 1:
        raise TooLittleDataReceivedError

    return non_empty_lines

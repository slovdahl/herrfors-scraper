# ruff: noqa: T201
"""Application main entry point."""

from datetime import date, timedelta

from herrfors_scraper.api import create_session, get_data
from herrfors_scraper.const import Type
from herrfors_scraper.exception import UnknownTypeError


def main(args: any) -> int:  # noqa: D103
    if len(args) != 5:
        print("Insufficient parameters.")
        print()
        print("Usage: \
              <usage place> \
              <customer number> \
              <days backwards> \
              <consumption|production>")

    usage_place = int(args[1])
    customer_number = int(args[2])
    days = args[3]

    if args[4] == "consumption":
        scrape_type = Type.CONSUMPTION
    elif args[4] == "production":
        scrape_type = Type.PRODUCTION
    else:
        raise UnknownTypeError

    to_date = date.today()  # noqa: DTZ011
    from_date = to_date - timedelta(days=days)

    session = create_session(usage_place=usage_place, customer_number=customer_number)
    data = get_data(session=session,
                    start=from_date,
                    end=to_date,
                    scrape_type=scrape_type)

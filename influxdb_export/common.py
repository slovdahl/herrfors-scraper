"""Common utilities."""
from __future__ import annotations

import csv
import sys
from datetime import datetime
from typing import TYPE_CHECKING

import dateutil
from influxdb import InfluxDBClient

if TYPE_CHECKING:
    from collections.abc import Callable

local_tz = dateutil.tz.gettz("Europe/Helsinki")


def parse_kwh_value(value_string: str) -> float:
    """Parse a decimal kWh value that may use a comma as decimal separator."""
    return float(value_string.strip().replace(",", "."))


def parse_measurement_timestamp(timestamp_string: str) -> datetime:
    """Parse measurement timestamp in the current CSV export format."""
    return datetime.strptime(timestamp_string.strip(), "%Y-%m-%d %H:%M")\
        .replace(tzinfo=local_tz)


def read_measurements_from_stdin(parse_timestamp: Callable[[str], datetime],
                                 ) -> list[dict[str, str | dict[str, float]]]:
    """Read and parse CSV measurements from stdin in Herrfors export format.

    Example:
    "Date";"kWh"
    "2025-09-21 00:00";"0,494"
    "2025-09-21 01:00";"0,803"

    """
    json_body = []
    reader = csv.reader(sys.stdin, delimiter=";", quotechar='"')

    for row in reader:
        if not row:
            continue

        # Skip header row, e.g. "Date";"kWh"
        if row[0].strip().lower() == "date":
            continue

        if len(row) != 2:
            print(f"Expected exactly 2 columns, got {len(row)}")
            sys.exit(1)

        full_timestamp_str, power_value_string = row
        timestamp_local_tz = parse_timestamp(full_timestamp_str)
        power_value_kwh = parse_kwh_value(power_value_string)

        json_body.append(to_measurement_entry(timestamp_local_tz, power_value_kwh))

    return json_body


def to_measurement_entry(timestamp_local_tz: datetime,
                         power_value_kwh: float) -> dict[str, str | dict[str, float]]:
    """Turn the input into a measurement entry."""
    return {
        "measurement": "kWh",
        "time": timestamp_local_tz.isoformat(timespec="seconds"),
        "fields": {
            "value": power_value_kwh,
        },
    }


def write_to_influx(database: str,
                    json_body: list[dict[str, str | dict[str, float]]],
                    ) -> None:
    """Write the given data points to the given database."""
    client = InfluxDBClient(host="localhost", port=8086)
    client.switch_database(database)

    client.write_points(
        points=json_body,
        time_precision="s",
        tags={
            "provider": "Herrfors",
            "source": "portal.herrfors.fi",
        },
    )

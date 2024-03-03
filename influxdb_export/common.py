"""Common utilities."""
from __future__ import annotations

from datetime import datetime

import dateutil
from influxdb import InfluxDBClient

local_tz = dateutil.tz.gettz("Europe/Helsinki")


def parse_measurement_date_hour(measurement_date: str,
                                measurement_hour: str) -> datetime:
    """Parse the measurement date and hour."""
    return datetime.strptime(measurement_date, "%d.%m.%Y")\
            .replace(tzinfo=local_tz)\
            .replace(hour=int(measurement_hour))


def to_measurement_entry(timestamp_local_tz: datetime,
                         power_value_kwh: float) -> dict[str, str]:
    """Turn the input into a measurement entry."""
    return {
        "measurement": "kWh",
        "time": timestamp_local_tz.isoformat(timespec="seconds"),
        "fields": {
            "value": power_value_kwh,
        },
    }


def write_to_influx(database: str, json_body: list[dict[str, str]]) -> None:
    """Write the given data points to the given database."""
    with InfluxDBClient(host="localhost", port=8086) as client:
        client.switch_database(database)

        client.write_points(
            points=json_body,
            time_precision="s",
            tags={
                "provider": "Herrfors",
                "source": "meter.katterno.fi",
            },
        )

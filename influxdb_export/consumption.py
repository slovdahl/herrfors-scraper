"""Consumption exporter."""

import sys
import traceback

from influxdb_export.common import (
    parse_measurement_date_hour,
    to_measurement_entry,
    write_to_influx,
)

written_rows = 0
json_body = []

try:
    for line in sys.stdin:
        # Example:
        # 31.05.2021 00-01;0,47
        # 31.05.2021 01-02;0,48
        # 31.05.2021 02-03;0,53
        # 31.05.2021 03-04;1,02

        if ";" not in line:
            print(f"Failed to parse consumption line '{line}', ignoring")
            continue

        try:
            full_timestamp_str, power_usage_string = line.split(";")
        except ValueError:
            print(f"Failed to parse consumption line '{line}'")
            traceback.print_exc(file=sys.stderr)
            sys.exit(1)

        measurement_date, measurement_hour_range = full_timestamp_str.split(" ")
        # This feels wrong, we should use the second one instead. But the Herrfors
        # web UI shows it like this.
        measurement_hour, _ = measurement_hour_range.split("-")

        timestamp_local_tz = parse_measurement_date_hour("%d.%m.%Y",
                                                         measurement_date,
                                                         measurement_hour)

        power_usage_kwh = float(power_usage_string.strip().replace(",", "."))

        json_body.append(to_measurement_entry(timestamp_local_tz, power_usage_kwh))

        written_rows += 1
except KeyboardInterrupt:
    sys.stdout.flush()

if json_body:
    write_to_influx("power_consumption", json_body)

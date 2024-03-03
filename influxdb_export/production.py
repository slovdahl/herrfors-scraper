"""Production exporter."""

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
        # 2023-06-26 00:00:00;0,00
        # 2023-06-26 01:00:00;0,00
        # 2023-06-26 02:00:00;0,00
        # 2023-06-26 03:00:00;0,00

        if ";" not in line:
            print(f"Failed to parse production line '{line}', ignoring")
            continue

        try:
            full_timestamp_str, power_production_string = line.split(";")
        except ValueError:
            print(f"Failed to parse production line '{line}'")
            traceback.print_exc(file=sys.stderr)
            sys.exit(1)

        measurement_date, measurement_hour_minute_second = full_timestamp_str.split(" ")

        # 2023-06-26 00:00:00 seems to mean the production between 00:00:00 and 01:00:00
        measurement_hour, _, _ = measurement_hour_minute_second.split(":")

        timestamp_local_tz = parse_measurement_date_hour(measurement_date,
                                                         measurement_hour)

        power_production_kwh = float(power_production_string.strip().replace(",", "."))

        json_body.append(to_measurement_entry(timestamp_local_tz, power_production_kwh))

        written_rows += 1
except KeyboardInterrupt:
    sys.stdout.flush()

if json_body:
    write_to_influx("power_production", json_body)

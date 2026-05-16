"""Consumption exporter."""

import sys

from influxdb_export.common import (
    parse_measurement_timestamp,
    read_measurements_from_stdin,
    write_to_influx,
)

try:
    json_body = read_measurements_from_stdin(parse_measurement_timestamp)
except KeyboardInterrupt:
    sys.stdout.flush()

if json_body:
    write_to_influx("power_consumption", json_body)

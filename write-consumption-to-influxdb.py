#!/usr/bin/env python3

import datetime
import sys
import traceback

import dateutil
from influxdb import InfluxDBClient

client = InfluxDBClient(host='localhost', port=8086)
client.switch_database('power_consumption')

local_tz = dateutil.tz.gettz('Europe/Helsinki')

written_rows = 0
json_body = []

try:
    for line in sys.stdin:
        # Example:
        # 31.05.2021 00-01;0,47
        # 31.05.2021 01-02;0,48
        # 31.05.2021 02-03;0,53
        # 31.05.2021 03-04;1,02

        try:
            full_timestamp_string, power_usage_string = line.split(';')
        except ValueError:
            print(f"Failed to parse consumption line '{line}'")
            traceback.print_exc(file=sys.stderr)
            sys.exit(1)

        measurement_date, measurement_hour_range = full_timestamp_string.split(' ')
        # This feels wrong, we should use the second one instead. But the Herrfors
        # web UI shows it like this.
        measurement_hour, _ = measurement_hour_range.split('-')

        timestamp_tzless = datetime.datetime.strptime(measurement_date, '%d.%m.%Y').replace(hour=int(measurement_hour))
        timestamp_local_tz = timestamp_tzless.replace(tzinfo=local_tz)

        power_usage_kwh = float(power_usage_string.strip().replace(',', '.'))

        json_body.append(
            {
                "measurement": "kWh",
                "time": timestamp_local_tz.isoformat(timespec='seconds'),
                "fields": {
                    "value": power_usage_kwh
                }
            }
        )

        written_rows += 1

except KeyboardInterrupt:
    sys.stdout.flush()
    pass

if json_body:
    client.write_points(
        points=json_body,
        time_precision='s',
        tags={
            "provider": "Herrfors",
            "source": "meter.katterno.fi"
        }
    )

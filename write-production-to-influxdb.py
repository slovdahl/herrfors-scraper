#!/usr/bin/env python3

import datetime
import sys
import traceback

import dateutil
from influxdb import InfluxDBClient

client = InfluxDBClient(host='localhost', port=8086)
client.switch_database('power_production')

local_tz = dateutil.tz.gettz('Europe/Helsinki')

written_rows = 0
json_body = []

try:
    for line in sys.stdin:
        # Example:
        # 2023-06-26 00:00:00;0,00
        # 2023-06-26 01:00:00;0,00
        # 2023-06-26 02:00:00;0,00
        # 2023-06-26 03:00:00;0,00

        if ';' not in line:
            print(f"Failed to parse production line '{line}', ignoring")

        try:
            full_timestamp_string, power_production_string = line.split(';')
        except ValueError:
            print(f"Failed to parse production line '{line}'")
            traceback.print_exc(file=sys.stderr)
            sys.exit(1)

        measurement_date, measurement_hour_minute_second = full_timestamp_string.split(' ')

        # 2023-06-26 00:00:00 seems to mean the production between 00:00:00 and 01:00:00
        measurement_hour, _, _ = measurement_hour_minute_second.split(':')

        timestamp_tzless = datetime.datetime.strptime(measurement_date, '%Y-%m-%d').replace(hour=int(measurement_hour))
        timestamp_local_tz = timestamp_tzless.replace(tzinfo=local_tz)

        power_production_kwh = float(power_production_string.strip().replace(',', '.'))

        json_body.append(
            {
                "measurement": "kWh",
                "time": timestamp_local_tz.isoformat(timespec='seconds'),
                "fields": {
                    "value": power_production_kwh
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

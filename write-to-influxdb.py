#!/usr/bin/env python3

import datetime
import dateutil
import sys
from influxdb import InfluxDBClient

client = InfluxDBClient(host='automation1.lovdahl.eu', port=8086)
client.switch_database('power_consumption')

local_tz = dateutil.tz.gettz('Europe/Helsinki')

written_rows = 0
json_body = []

try:
    for line in sys.stdin:
        timestamp_string, _, power_usage_string = line.split(';')

        timestamp_tzless = datetime.datetime.strptime(timestamp_string, '%Y-%m-%d %H:%M:%S')
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

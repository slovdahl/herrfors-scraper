#!/usr/bin/env python3

import datetime
import sys

import requests


if len(sys.argv) != 5:
    print("Insufficient parameters")
    print("Usage: ./scrape.py <usage place> <customer number> <date> <consumption|production>")
    sys.exit(1)

usage_place = int(sys.argv[1])
customer_number = int(sys.argv[2])
date = sys.argv[3]
date_obj = datetime.datetime.strptime(date, '%Y-%m-%d')
scrape_type = sys.argv[4]

from_date = date_obj.strftime('%d.%m.%Y')
to_date = (date_obj + datetime.timedelta(1)).strftime('%d.%m.%Y')

s = requests.Session()

login_payload = {
    'usageplace': usage_place,
    'customernumber': customer_number
}

login_result = s.post('https://meter.katterno.fi/index.php',
                      data=login_payload,
                      allow_redirects=False)

if login_result.status_code != 302:
    print("Failed to log in")
    print("Headers:", login_result.headers)
    sys.exit(2)


if scrape_type == 'production':
    export_type = 'production'
else:
    export_type = 'hours'

export_payload = {
    'exporttype': export_type,
    'export-range': from_date + ' - ' + to_date
}

result = s.post('https://meter.katterno.fi/export.php',
                data=export_payload,
                allow_redirects=False)

if result.status_code != 200 or (
        'Content-Disposition' not in result.headers and
        'content-disposition' not in result.headers
    ):
    print("Unexpected HTTP response:", result.status_code)
    print("Headers:", result.headers)
    sys.exit(3)

non_empty_lines = [line for line in result.text.split("\n") if line.strip() != ""]

if len(non_empty_lines) == 0:
    print("No data received")
    sys.exit(4)

if len(non_empty_lines) <= 1:
    print("Only received one line of data")
    sys.exit(5)

print("\n".join(non_empty_lines))

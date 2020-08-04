#!/usr/bin/env python3

import datetime
import os
import requests
import sys

if len(sys.argv) != 4:
    print("Insufficient parameters")
    print("Usage: ./scrape.py <usage place> <customer number> <date>")
    sys.exit(1)

usage_place = int(sys.argv[1])
customer_number = int(sys.argv[2])
date = sys.argv[3]
date_obj = datetime.datetime.strptime(date, '%Y-%m-%d')

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

export_payload = {
    'exporttype': 'hours',
    'export-range': from_date + ' - ' + to_date
}

result = s.post('https://meter.katterno.fi/export.php',
                data=export_payload,
                allow_redirects=False)

if result.status_code != 200 or not result.headers['Content-Disposition']:
    sys.exit(3)

non_empty_lines = [line for line in result.text.split("\n") if line.strip() != ""]

print("\n".join(non_empty_lines))

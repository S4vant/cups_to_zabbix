#!/usr/bin/env python3

import re
import json
import socket
import subprocess

from datetime import datetime

LOGFILE = "/home/ya.ryazancev/cups_to_zabbix/tmp/cups2.log"

HOST = 'cups-demo'

ZABBIX_SERVER = "localhost"
ZABBIX_PORT = "10051"

RAW_ITEM_KEY = "cups.jobs.raw"

pattern = re.compile(
    r'^(?P<printer>\S+)\s+'
    r'(?P<user>\S+)\s+'
    r'(?P<job_id>\d+)\s+'
    r'\[(?P<time>[^\]]+)\]\s+'
    r'total\s+(?P<pages>\d+)\s+-\s+'
    r'localhost\s+'
    r'(?P<rest>.+)$'
)


def extract_filename(rest: str) -> str:

    rest = re.sub(r'\s+-\s+-\s*$', '', rest)
    rest = re.sub(r'\s+A4\s+one-sided\s*$', '', rest)
    rest = re.sub(r'\s+[—-]\s+Scanned Document\s*$', '', rest)

    return rest.strip()


def parse_cups_time(timestr: str):

    dt = datetime.strptime(
        timestr,
        "%d/%b/%Y:%H:%M:%S %z"
    )

    return {
        "timestamp": int(dt.timestamp()),
        "iso": dt.isoformat()
    }


jobs = []

with open(LOGFILE, encoding="utf-8") as f:

    for line in f:

        line = line.strip()

        if not line:
            continue

        m = pattern.match(line)

        if not m:
            continue

        printer = m.group("printer")
        user = m.group("user")
        job_id = int(m.group("job_id"))
        pages = int(m.group("pages"))

        raw_time = m.group("time")
        parsed_time = parse_cups_time(raw_time)

        rest = m.group("rest")
        file_name = extract_filename(rest)

        jobs.append({
            "host": HOST,
            "user": user,
            "printer": printer,
            "job_id": job_id,
            "file": file_name,
            "pages": pages,
            "timestamp": parsed_time["timestamp"],
            "datetime": parsed_time["iso"]
        })


payload = {
    "jobs": jobs
}


json_data = json.dumps(
    payload,
    ensure_ascii=False
)


subprocess.run([
    "zabbix_sender",
    "-z", ZABBIX_SERVER,
    "-p", ZABBIX_PORT,
    "-s", HOST,
    "-k", RAW_ITEM_KEY,
    "-o", json_data
])


print("sent")
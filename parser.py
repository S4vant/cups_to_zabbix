#!/usr/bin/env python3

import re
import json
import subprocess
import socket
from collections import defaultdict

LOGFILE = "/tmp/cups.log"

HOST = "cups-demo"
SERVER = "localhost"

pattern = re.compile(
    r"^(.*?)\s+([\w\.-]+)\s+(\d+)\s+\[(.*?)\]\s+total\s+(\d+)\s+-\s+localhost\s+(.*?)\s+"
)

users = defaultdict(int)
pages_total = 0
jobs_count = 0
jobs_raw = []

hostname = socket.gethostname()


with open(LOGFILE, encoding="utf-8") as f:
    for line in f:
        line = line.strip()

        m = pattern.match(line)
        if not m:
            continue

        printer = m.group(1)
        user = m.group(2)
        job_id = m.group(3)
        time = m.group(4)
        pages = int(m.group(5))
        file_name = m.group(6).split(" - ")[0]

        users[user] += 1
        pages_total += pages
        jobs_count += 1

        jobs_raw.append({
            "printer": printer,
            "user": user,
            "job_id": job_id,
            "pages": pages,
            "file": file_name,
            "time": time
        })


payload = {
    "host": hostname,
    "users": list(users.keys()),
    "jobs_count": jobs_count,
    "pages_total": pages_total,
    "jobs": jobs_raw
}

json_data = json.dumps(payload, ensure_ascii=False)


subprocess.run([
    "zabbix_sender",
    "-z", SERVER,
    "-p", "10051",
    "-s", HOST,
    "-k", "cups.jobs.raw",
    "-o", json_data
])


subprocess.run([
    "zabbix_sender",
    "-z", SERVER,
    "-p", "10051",
    "-s", HOST,
    "-k", "cups.users",
    "-o", ",".join(users.keys())
])


subprocess.run([
    "zabbix_sender",
    "-z", SERVER,
    "-p", "10051",
    "-s", HOST,
    "-k", "cups.jobs.count",
    "-o", str(jobs_count)
])


subprocess.run([
    "zabbix_sender",
    "-z", SERVER,
    "-p", "10051",
    "-s", HOST,
    "-k", "cups.pages.total",
    "-o", str(pages_total)
])


print("sent")
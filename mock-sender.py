#!/usr/bin/env python3

import json
import subprocess

HOST = "cups-demo"
SERVER = "localhost"
PORT = "10051"

with open("mock_jobs.json", encoding="utf-8") as f:
    data = json.load(f)

jobs = data["jobs"]

pages_total = sum(j["pages"] for j in jobs)
users_count = len(set(j["user"] for j in jobs))
jobs_count = len(jobs)

payload = json.dumps(data, ensure_ascii=False)

metrics = [
    ("cups.jobs.raw", payload),
    ("cups.jobs.count", str(jobs_count)),
    ("cups.pages.total", str(pages_total)),
    ("cups.users.count", str(users_count))
]

for key, value in metrics:

    subprocess.run([
        "zabbix_sender",
        "-z", SERVER,
        "-p", PORT,
        "-s", HOST,
        "-k", key,
        "-o", value
    ])

print("mock data sent")
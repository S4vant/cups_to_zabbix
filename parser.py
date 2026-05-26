#!/usr/bin/env python3

import re
import json
import socket
from collections import defaultdict

LOGFILE = "cups.log"   # сюда вставить файл с логами

hostname = socket.gethostname()

result = {
    "host": hostname,
    "users": {}
}

pattern = re.compile(
    r"^(.*?)\s+([\w\.-]+)\s+(\d+)\s+(.*)$"
)

with open(LOGFILE, encoding="utf-8") as f:
    for line in f:
        line = line.strip()

        m = pattern.match(line)
        if not m:
            continue

        printer_job = m.group(1)
        user = m.group(2)
        size = int(m.group(3))
        date = m.group(4)

        # выделяем job_id
        job_match = re.search(r'-(\d+)$', printer_job)

        job_id = job_match.group(1) if job_match else "unknown"

        printer = re.sub(r'-\d+$', '', printer_job)

        entry = {
            "job_id": job_id,
            "printer": printer,
            "file": "unknown",
            "pages": "unknown",
            "bytes": size,
            "date": date
        }

        if user not in result["users"]:
            result["users"][user] = []

        result["users"][user].append(entry)


print(json.dumps(result, indent=4, ensure_ascii=False))
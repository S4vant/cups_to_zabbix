#!/usr/bin/env python3

import re
import json
import subprocess
from collections import defaultdict

LOGFILE = "tmp/cups2.log"

HOST = "cups-demo"
SERVER = "localhost"
PORT = "10051"

# Формат:
# printer user jobid [date] total pages - localhost rest...
#
# Пример:
# Generic-IPP-Everywhere i.vdovkin 32 [15/May/2026:16:35:43 +0400] total 1 - localhost Согласие на обработку персональных данных.docx A4 one-sided

pattern = re.compile(
    r'^(?P<printer>\S+)\s+'
    r'(?P<user>\S+)\s+'
    r'(?P<job_id>\d+)\s+'
    r'\[(?P<time>[^\]]+)\]\s+'
    r'total\s+(?P<pages>\d+)\s+-\s+'
    r'localhost\s+'
    r'(?P<rest>.+)$'
)

users = defaultdict(int)

pages_total = 0
jobs_count = 0
jobs_raw = []


def extract_filename(rest: str) -> str:
    """
    Извлекает имя файла из хвоста строки.
    Убирает типовые окончания:
      - A4 one-sided
      - - -
      - Scanned Document
    """

    # Убираем хвосты вида " - -"
    rest = re.sub(r'\s+-\s+-\s*$', '', rest)

    # Убираем хвост "A4 one-sided"
    rest = re.sub(r'\s+A4\s+one-sided\s*$', '', rest)

    # Иногда встречается:
    # filename.pdf — Scanned Document
    rest = re.sub(r'\s+[—-]\s+Scanned Document\s*$', '', rest)

    return rest.strip()


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
        job_id = m.group("job_id")
        time = m.group("time")
        pages = int(m.group("pages"))

        rest = m.group("rest")
        file_name = extract_filename(rest)

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
    "jobs": jobs_raw
}

json_data = json.dumps(payload, ensure_ascii=False)


def send_to_zabbix(key: str, value: str):
    subprocess.run([
        "zabbix_sender",
        "-z", SERVER,
        "-p", PORT,
        "-s", HOST,
        "-k", key,
        "-o", value
    ])


# RAW JSON
# send_to_zabbix(
#     "cups.jobs.raw",
#     json_data
# )

# # Список пользователей
# send_to_zabbix(
#     "cups.users",
#     ",".join(users.keys())
# )

# # Количество задач
# send_to_zabbix(
#     "cups.jobs.count",
#     str(jobs_count)
# )

# # Всего страниц
# send_to_zabbix(
#     "cups.pages.total",
#     str(pages_total)
# )

print(payload)
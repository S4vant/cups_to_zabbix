#!/usr/bin/env python3

import re
import subprocess
import sys

####################################
# НАСТРОЙКИ
####################################

ZABBIX_SERVER = "192.168.1.10"
HOSTNAME = "cups-demo"

LOGFILE = "/tmp/cups.log"

####################################


def send(key, value):

    cmd = [
        "zabbix_sender",
        "-z", ZABBIX_SERVER,
        "-s", HOSTNAME,
        "-k", key,
        "-o", str(value)
    ]

    r = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    print(
        f"{key}: {value}"
    )

    if r.returncode != 0:
        print(
            "ERROR:",
            r.stderr
        )


try:

    with open(
        LOGFILE,
        encoding="utf8"
    ) as f:

        lines = [
            x.strip()
            for x in f.readlines()
            if x.strip()
        ]

except:

    print(
        "Нет файла логов"
    )

    sys.exit(1)


jobs = []
users = set()
printers = set()

pattern = re.compile(
    r"^(.*?)\s+([\w\.-]+)\s+(\d+)\s+(.*)$"
)

for line in lines:

    m = pattern.match(line)

    if not m:
        continue


    printer_job = m.group(1)

    user = m.group(2)

    bytes_size = int(
        m.group(3)
    )

    date = m.group(4)


    job_match = re.search(
        r'-(\d+)$',
        printer_job
    )

    job = (
        job_match.group(1)
        if job_match
        else "0"
    )


    printer = re.sub(
        r'-\d+$',
        '',
        printer_job
    )


    jobs.append({

        "user":
            user,

        "printer":
            printer,

        "job":
            job,

        "bytes":
            bytes_size,

        "date":
            date

    })


    users.add(
        user
    )

    printers.add(
        printer
    )


if not jobs:

    print(
        "Нет заданий"
    )

    sys.exit()


last = jobs[-1]


####################################
# ПОСЛЕДНЕЕ ЗАДАНИЕ
####################################


send(
    "cups.last.user",
    last["user"]
)


send(
    "cups.last.printer",
    last["printer"]
)


send(
    "cups.last.job",
    last["job"]
)


send(
    "cups.last.bytes",
    last["bytes"]
)


send(
    "cups.last.date",
    last["date"]
)


####################################
# ОБЩАЯ СТАТИСТИКА
####################################


send(
    "cups.jobs.count",
    len(jobs)
)


send(
    "cups.total.bytes",
    sum(
        x["bytes"]
        for x in jobs
    )
)


send(
    "cups.unique.users",
    len(users)
)


send(
    "cups.unique.printers",
    len(printers)
)


print(
    "\nDONE"
)
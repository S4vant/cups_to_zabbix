#!/usr/bin/env python3

import re
import json
import subprocess
import socket

LOGFILE = "/tmp/cups.log"

HOST = "cups-demo"

SERVER = "127.0.0.1"


jobs = []

hostname = socket.gethostname()


pattern = re.compile(
    r"^(.*?)\s+([\w\.-]+)\s+(\d+)\s+(.*)$"
)


with open(
    LOGFILE,
    encoding="utf8"
) as f:

    for line in f:

        line = line.strip()

        m = pattern.match(
            line
        )

        if not m:

            continue


        printer_job = m.group(
            1
        )

        user = m.group(
            2
        )

        bytes_size = int(
            m.group(
                3
            )
        )

        date = m.group(
            4
        )


        job_match = re.search(
            r'-(\d+)$',
            printer_job
        )

        job_id = (
            job_match.group(
                1
            )
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

            "job":

                job_id,

            "printer":
                printer,

            "bytes":
                bytes_size,

            "date":
                date

        })


payload = {

    "hostname":
        hostname,

    "jobs":
        jobs

}


data = json.dumps(
    payload,
    ensure_ascii=False
)



subprocess.run([

    "zabbix_sender",

    "-z",
    SERVER,

    "-s",
    HOST,

    "-k",
    "cups.jobs.json",

    "-o",
    data

])


print(

    "Отправлено"

)
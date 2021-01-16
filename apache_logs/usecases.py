from datetime import datetime

import requests

from apache_logs.daos import ApacheLogsDao
from apache_logs.entities import ApacheLog


class ParseLogsUseCase:
    def __init__(self, parse_logs_dao: ApacheLogsDao):
        self.dao = parse_logs_dao

    def execute(self, url):
        result = requests.get(url)
        apache_logs = []

        for line in result.iter_lines():
            if not line:
                continue
            line = line.decode("utf-8")
            ip_address, _, _, date, gmt, method, uri, _, status_code, size, *options = line.split()
            date = date[1:]
            gmt = gmt[:-1]
            method = method[1:]
            date = datetime.strptime(date + gmt, '%d/%b/%Y:%H:%M:%S%z')

            apache_log = ApacheLog(
                ip_address=ip_address,
                date=date,
                method=method,
                uri=uri,
                status_code=status_code,
                size=size,
            )

            apache_logs.append(apache_log)

        self.dao.create_apache_logs(logs=apache_logs)

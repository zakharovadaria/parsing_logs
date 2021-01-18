import ipaddress
from datetime import datetime

import requests

from apache_logs.daos import ApacheLogsDao
from apache_logs.entities import ApacheLog, LogStatistics, PaginatedLogWithStatistics


class ParseLogsUseCase:

    def __init__(self, logs_dao: ApacheLogsDao):
        self.dao = logs_dao

    def execute(self, url: str) -> None:
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
            status_code = int(status_code)

            try:
                size = int(size)
            except ValueError:
                size = 0

            try:
                ip_address = str(ipaddress.ip_address(ip_address))
            except ValueError:
                print(f"{ip_address} is not a valid ip address")
                continue

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


class GetLogsUseCase:

    def __init__(self, logs_dao: ApacheLogsDao):
        self.dao = logs_dao

    def execute(self, query: str, page: int) -> PaginatedLogWithStatistics:
        logs, pagination = self.dao.get_logs(page=page, query=query)

        unique_ip_count = self.dao.get_count_unique_ip_addresses(query=query)
        top_ip_addresses = self.dao.get_top_ip_addresses(query=query)
        http_methods_count = self.dao.get_http_methods_count(query=query)
        sum_sizes = self.dao.get_sum_sizes(query=query)

        statistics = LogStatistics(
            unique_ip_count=unique_ip_count,
            top_ip_addresses=top_ip_addresses,
            http_methods_count=http_methods_count,
            sum_sizes=sum_sizes,
        )

        return PaginatedLogWithStatistics(logs=logs, statistics=statistics, pagination=pagination)

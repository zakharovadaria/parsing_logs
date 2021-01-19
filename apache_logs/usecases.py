import ipaddress
from datetime import datetime
from math import ceil
from typing import List

from apache_logs.constants import HTTP_METHODS
from apache_logs.entities import ApacheLog, LogStatistics, PaginatedLogWithStatistics, ImportStatus
from apache_logs.interfaces import IApacheLogsDAO, IRequestDAO, IImportStatusDAO


class ParseLogsUseCase:

    def __init__(self, logs_dao: IApacheLogsDAO, request_dao: IRequestDAO, import_status_dao: IImportStatusDAO):
        self.logs_dao = logs_dao
        self.request_dao = request_dao
        self.import_status_dao = import_status_dao

    def _import_logs(self, rows: List[str]):
        apache_logs = []

        for line in rows:
            if not line:
                continue
            ip_address, _, _, date, gmt, method, uri, _, status_code, size, *options = line.split()

            try:
                ip_address = str(ipaddress.ip_address(ip_address))
            except ValueError:
                print(f"{ip_address} is not a valid ip address")
                continue

            date = date[1:]
            gmt = gmt[:-1]

            try:
                date = datetime.strptime(date + gmt, '%d/%b/%Y:%H:%M:%S%z')
            except ValueError:
                print(f"{date} date is not a valid date.")
                continue

            method = method[1:]

            if method not in HTTP_METHODS:
                print(f"{method} method is not valid.")
                continue

            try:
                status_code = int(status_code)
            except ValueError:
                print(f"{status_code} should be valid integer")
                continue

            if not 100 <= status_code <= 599:
                print(f"{status_code} should be between 100 and 599")
                continue

            try:
                size = int(size)
            except ValueError:
                size = 0

            apache_log = ApacheLog(
                ip_address=ip_address,
                date=date,
                method=method,
                uri=uri,
                status_code=status_code,
                size=size,
            )

            apache_logs.append(apache_log)

        self.logs_dao.create_apache_logs(apache_logs=apache_logs)

    def execute(self, url: str) -> None:
        is_accept_ranges, max_length = self.request_dao.check_partial_content(url=url)

        import_status = self.import_status_dao.create_import_status()

        if is_accept_ranges:
            step = ceil(max_length / 100)
            percent = 0
            from_bytes = 0
            to_bytes = step
            last_row = ""

            while True:
                rows = self.request_dao.get_partial_rows(url=url, from_bytes=from_bytes, to_bytes=to_bytes)
                if last_row:
                    rows[0] = f"{last_row}{rows[0]}"
                last_row = rows[-1]
                self._import_logs(rows=rows[:-1])

                if to_bytes == max_length:
                    self.import_status_dao.finish_import_status(import_status_id=import_status.pk)
                    return

                percent += 1

                self.import_status_dao.update_import_status(import_status_id=import_status.pk, percent=percent)

                from_bytes += step
                to_bytes += step

                if to_bytes > max_length:
                    to_bytes = max_length
        else:
            rows = self.request_dao.get_full_rows(url=url)
            self._import_logs(rows=rows)
            self.import_status_dao.finish_import_status(import_status_id=import_status.pk)


class GetLogsUseCase:

    def __init__(self, logs_dao: IApacheLogsDAO):
        self.dao = logs_dao

    def execute(self, query: str, page: int, per_page: int = 25) -> PaginatedLogWithStatistics:
        logs, pagination = self.dao.get_logs(page=page, query=query, per_page=per_page)

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


class ImportStatusUseCase:
    def __init__(self, dao: IImportStatusDAO):
        self.dao = dao

    def execute(self) -> List[ImportStatus]:
        import_statuses = self.dao.get_import_statuses()

        return import_statuses

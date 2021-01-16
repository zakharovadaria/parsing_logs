from typing import List

from apache_logs.entities import ApacheLog
from apache_logs.models import ApacheLogORM


class ApacheLogsDao:
    def create_apache_logs(self, logs: List[ApacheLog]):
        db_logs = []

        for log in logs:
            db_logs.append(ApacheLogORM(
                ip_address=log.ip_address,
                date=log.date,
                method=log.method,
                uri=log.uri,
                status_code=log.status_code,
                size=log.size,
            ))

        ApacheLogORM.objects.bulk_create(db_logs)

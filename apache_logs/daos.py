from typing import List, Optional, Tuple

import requests
from django.core.paginator import Paginator
from django.db.models import Count, Sum, QuerySet, Q

from apache_logs.entities import ApacheLog, CountIPAddress, CountMethod, Pagination, ImportStatus
from apache_logs.interfaces import IRequestDAO, IImportStatusDAO, IApacheLogsDAO
from apache_logs.models import ApacheLogORM, ImportStatusORM


class ApacheLogsDAO(IApacheLogsDAO):

    def create_apache_logs(self, apache_logs: List[ApacheLog]):
        db_logs = [
            ApacheLogORM(
                ip_address=log.ip_address,
                date=log.date,
                method=log.method,
                uri=log.uri,
                status_code=log.status_code,
                size=log.size,
            ) for log in apache_logs
        ]

        ApacheLogORM.objects.bulk_create(db_logs)

    def _get_queryset_with_search_string(self, *, query: str) -> QuerySet:
        return ApacheLogORM.objects.filter(
            Q(ip_address__icontains=query) |
            Q(date__icontains=query) |
            Q(method__icontains=query) |
            Q(uri__icontains=query)
        )

    def get_count_unique_ip_addresses(self, *, query: Optional[str]) -> int:
        # Example on SQL:
        # SELECT COUNT(DISTINCT ip_address) FROM apache_logs_apachelogorm;
        return (self._get_queryset_with_search_string(query=query)
                    .values("ip_address")
                    .distinct("ip_address")
                    .count())

    def get_top_ip_addresses(self, *, addresses_count: int = 10, query: Optional[str]) -> List[CountIPAddress]:
        # Example on SQL:
        # SELECT ip_address, COUNT(ip_address) AS ip_address_count
        # FROM apache_logs_apachelogorm
        # GROUP BY ip_address
        # ORDER BY ip_address_count DESC
        # LIMIT 10;

        count_ip_addresses = (self._get_queryset_with_search_string(query=query).values("ip_address")
                                                                                .annotate(count=Count("ip_address"))
                                                                                .order_by("-count")[:addresses_count])
        entity_count_ip_address = [
            CountIPAddress(ip_address=count_ip_address["ip_address"], count=count_ip_address["count"])
            for count_ip_address in count_ip_addresses
        ]

        return entity_count_ip_address

    def get_http_methods_count(self, *, query: Optional[str]) -> List[CountMethod]:
        # Example on SQL:
        # SELECT method, COUNT(method)
        # FROM apache_logs_apachelogorm
        # GROUP BY method;

        count_methods = (self._get_queryset_with_search_string(query=query).values("method")
                                                                           .annotate(count=Count("method")))

        entity_count_methods = [
            CountMethod(method=count_method["method"], count=count_method["count"])
            for count_method in count_methods
        ]

        return entity_count_methods

    def get_sum_sizes(self, *, query: Optional[str]) -> int:
        # Example on SQL:
        # SELECT SUM(method)
        # FROM apache_logs_apachelogorm;

        total_size = self._get_queryset_with_search_string(query=query).aggregate(total_size=Sum('size'))

        return total_size["total_size"] or 0

    def get_logs(self, *, page: int, per_page: int, query: Optional[str]) -> Tuple[List[ApacheLog], Pagination]:
        queryset = self._get_queryset_with_search_string(query=query).order_by("id").all()

        logs = Paginator(queryset, per_page=per_page)

        logs = logs.get_page(page)

        entity_logs = [
            ApacheLog(
                ip_address=log.ip_address,
                date=log.date,
                method=log.method,
                uri=log.uri,
                status_code=log.status_code,
                size=log.size,
            ) for log in logs.object_list
        ]

        pagination = Pagination(
            page_range=list(logs.paginator.page_range),
            has_other_pages=logs.has_other_pages(),
            has_previous=logs.has_previous(),
            previous_page_number=logs.previous_page_number() if logs.has_previous() else 0,
            number=logs.number,
            num_pages=logs.paginator.num_pages,
            has_next=logs.has_next(),
            next_page_number=logs.next_page_number() if logs.has_next() else 0,
        )
        return entity_logs, pagination


class RequestDAO(IRequestDAO):

    def check_partial_content(self, url: str) -> Tuple[bool, int]:
        headers = requests.head(url)
        is_accept_ranges = False
        max_length = 0
        if "Accept-Ranges" in headers.headers:
            is_accept_ranges = True
            max_length = int(headers.headers["Content-Length"])

        return is_accept_ranges, max_length

    def get_partial_rows(self, url: str, from_bytes: int, to_bytes: int) -> List[str]:
        result = requests.get(url, headers={"Range": f"bytes={from_bytes}-{to_bytes}"})
        rows = result.content.decode("utf-8").split("\n")

        return rows

    def get_full_rows(self, url: str) -> List[str]:
        result = requests.get(url)
        rows = result.content.decode("utf-8").split("\n")

        return rows


class ImportStatusDAO(IImportStatusDAO):
    def create_import_status(self) -> ImportStatus:
        import_status = ImportStatusORM()
        import_status.save()
        return ImportStatus(pk=import_status.pk, percent=import_status.percent, status=import_status.status)

    def update_import_status(self, import_status_id: int, percent: int) -> ImportStatus:
        import_status = ImportStatusORM.objects.get(pk=import_status_id)
        import_status.percent = percent
        import_status.save()
        return ImportStatus(pk=import_status.pk, percent=import_status.percent, status=import_status.status)

    def finish_import_status(self, import_status_id: int) -> ImportStatus:
        import_status = ImportStatusORM.objects.get(pk=import_status_id)
        import_status.status = ImportStatusORM.STATUS_FINISH
        import_status.percent = 100
        import_status.save()
        return ImportStatus(pk=import_status.pk, percent=import_status.percent, status=import_status.status)

    def get_import_statuses(self) -> List[ImportStatus]:
        import_statuses = ImportStatusORM.objects.all()

        return [
            ImportStatus(
                pk=import_status.pk,
                percent=import_status.percent,
                status=import_status.status,
            ) for import_status in import_statuses
        ]

from typing import List, Optional, Tuple

from django.core.paginator import Paginator
from django.db.models import Count, Sum, QuerySet, Q

from apache_logs.entities import ApacheLog, CountIPAddress, CountMethod, Pagination
from apache_logs.models import ApacheLogORM


class ApacheLogsDao:

    def create_apache_logs(self, logs: List[ApacheLog]):
        db_logs = [
            ApacheLogORM(
                ip_address=log.ip_address,
                date=log.date,
                method=log.method,
                uri=log.uri,
                status_code=log.status_code,
                size=log.size,
            ) for log in logs
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

        return total_size["total_size"]

    def get_logs(self, *, page: int, query: Optional[str]) -> Tuple[List[ApacheLog], Pagination]:
        queryset = self._get_queryset_with_search_string(query=query).order_by("id").all()

        logs = Paginator(queryset, per_page=25)

        logs = logs.get_page(page)

        entity_logs = [ApacheLog(
            ip_address=log.ip_address,
            date=log.date,
            method=log.method,
            uri=log.uri,
            status_code=log.status_code,
            size=log.size,
        ) for log in logs.object_list]

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

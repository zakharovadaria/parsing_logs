import datetime
from dataclasses import dataclass
from typing import List


@dataclass
class ApacheLog:
    ip_address: str
    date: datetime
    method: str
    uri: str
    status_code: int
    size: int


@dataclass
class CountIPAddress:
    ip_address: str
    count: int


@dataclass
class CountMethod:
    method: str
    count: int


@dataclass
class LogStatistics:
    unique_ip_count: int
    top_ip_addresses: List[CountIPAddress]
    http_methods_count: List[CountMethod]
    sum_sizes: int


@dataclass
class Pagination:
    has_other_pages: bool
    has_previous: bool
    previous_page_number: int
    number: int
    num_pages: int
    has_next: bool
    next_page_number: int
    page_range: List[int]


@dataclass
class PaginatedLogWithStatistics:
    logs: List[ApacheLog]
    statistics: LogStatistics
    pagination: Pagination


@dataclass
class ImportStatus:
    pk: int
    percent: int
    status: str

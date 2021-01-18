from abc import ABC, abstractmethod
from typing import List, Tuple, Optional

from apache_logs.entities import ApacheLog, CountIPAddress, CountMethod, Pagination, ImportStatus


class IApacheLogsDAO(ABC):
    @abstractmethod
    def create_apache_logs(self, apache_logs: List[ApacheLog]):
        pass

    @abstractmethod
    def get_count_unique_ip_addresses(self, *, query: Optional[str]) -> int:
        pass

    @abstractmethod
    def get_top_ip_addresses(self, *, addresses_count: int = 10, query: Optional[str]) -> List[CountIPAddress]:
        pass

    @abstractmethod
    def get_http_methods_count(self, *, query: Optional[str]) -> List[CountMethod]:
        pass

    @abstractmethod
    def get_sum_sizes(self, *, query: Optional[str]) -> int:
        pass

    @abstractmethod
    def get_logs(self, *, page: int, per_page: int, query: Optional[str]) -> Tuple[List[ApacheLog], Pagination]:
        pass


class IRequestDAO(ABC):
    @abstractmethod
    def check_partial_content(self, url: str) -> Tuple[bool, int]:
        pass

    @abstractmethod
    def get_partial_rows(self, url: str, from_bytes: int, to_bytes: int) -> List[str]:
        pass

    @abstractmethod
    def get_full_rows(self, url: str) -> List[str]:
        pass


class IImportStatusDAO(ABC):
    @abstractmethod
    def create_import_status(self) -> ImportStatus:
        pass

    @abstractmethod
    def update_import_status(self, import_status_id: int, percent: int) -> ImportStatus:
        pass

    @abstractmethod
    def finish_import_status(self, import_status_id: int) -> ImportStatus:
        pass

    @abstractmethod
    def get_import_statuses(self) -> List[ImportStatus]:
        pass

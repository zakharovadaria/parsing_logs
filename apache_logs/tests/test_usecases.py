from datetime import datetime
from unittest import TestCase, mock

from apache_logs.entities import ApacheLog, CountIPAddress, CountMethod, Pagination, PaginatedLogWithStatistics, \
    LogStatistics
from apache_logs.usecases import ParseLogsUseCase, GetLogsUseCase, ImportStatusUseCase


class ParseLogsUseCaseTestCase(TestCase):
    def setUp(self) -> None:
        self.logs_dao = mock.Mock()
        self.request_dao = mock.Mock()
        self.import_status_dao = mock.Mock()

    def test_execute_no_accept_ranges(self):
        usecase = ParseLogsUseCase(self.logs_dao, self.request_dao, self.import_status_dao)
        usecase._import_logs = mock.Mock()
        url = mock.Mock()
        self.request_dao.check_partial_content.return_value = (False, 0)
        self.request_dao.get_full_rows.return_value = []
        import_status_mock = mock.Mock()
        self.import_status_dao.create_import_status.return_value = import_status_mock

        usecase.execute(url)

        self.request_dao.check_partial_content.assert_called_once_with(url=url)
        self.import_status_dao.create_import_status.assert_called_once_with()
        self.request_dao.get_full_rows.assert_called_once_with(url=url)
        self.request_dao.get_partial_rows.assert_not_called()
        self.import_status_dao.finish_import_status.assert_called_once_with(import_status_id=import_status_mock.pk)
        self.import_status_dao.update_import_status.assert_not_called()
        usecase._import_logs.assert_called_once_with(rows=[])

    def test_execute_accept_ranges(self):
        usecase = ParseLogsUseCase(self.logs_dao, self.request_dao, self.import_status_dao)
        usecase._import_logs = mock.Mock()
        url = mock.Mock()
        self.request_dao.check_partial_content.return_value = (True, 100)
        import_status_mock = mock.Mock()
        self.import_status_dao.create_import_status.return_value = import_status_mock
        self.request_dao.get_partial_rows.return_value = ["first", "second"]
        usecase.execute(url)

        self.request_dao.check_partial_content.assert_called_once_with(url=url)
        self.import_status_dao.create_import_status.assert_called_once_with()
        self.request_dao.get_full_rows.assert_not_called()
        self.assertEqual(self.request_dao.get_partial_rows.call_count, 100)
        self.import_status_dao.finish_import_status.assert_called_once_with(import_status_id=import_status_mock.pk)
        self.assertEqual(self.import_status_dao.update_import_status.call_count, 99)
        self.assertEqual(usecase._import_logs.call_count, 100)

    def test_import_logs_empty_rows(self):
        usecase = ParseLogsUseCase(self.logs_dao, self.request_dao, self.import_status_dao)

        usecase._import_logs(rows=[])

        self.logs_dao.create_apache_logs.assert_called_once_with(apache_logs=[])

    def test_import_logs_invalid_ip_address(self):
        usecase = ParseLogsUseCase(self.logs_dao, self.request_dao, self.import_status_dao)

        usecase._import_logs(rows=["ip - - [12/Jan/2020:12:12:12 +0100] \"GET /index - 200 123"])

        self.logs_dao.create_apache_logs.assert_called_once_with(apache_logs=[])

    def test_import_logs_invalid_date(self):
        usecase = ParseLogsUseCase(self.logs_dao, self.request_dao, self.import_status_dao)

        usecase._import_logs(rows=["127.0.0.1 - - [12/JJan/2020:12:12:12 +0100] \"GET /index - 200 123"])

        self.logs_dao.create_apache_logs.assert_called_once_with(apache_logs=[])

    def test_import_logs_invalid_method(self):
        usecase = ParseLogsUseCase(self.logs_dao, self.request_dao, self.import_status_dao)

        usecase._import_logs(rows=["127.0.0.1 - - [19/Dec/2020:13:57:26 +0100] \"METHOD /index - 200 123"])

        self.logs_dao.create_apache_logs.assert_called_once_with(apache_logs=[])

    def test_import_logs_invalid_status_code(self):
        usecase = ParseLogsUseCase(self.logs_dao, self.request_dao, self.import_status_dao)

        usecase._import_logs(rows=["127.0.0.1 - - [19/Dec/2020:13:57:26 +0100] \"GET /index - status 123"])

        self.logs_dao.create_apache_logs.assert_called_once_with(apache_logs=[])

    def test_import_logs(self):
        usecase = ParseLogsUseCase(self.logs_dao, self.request_dao, self.import_status_dao)

        usecase._import_logs(rows=["127.0.0.1 - - [19/Dec/2020:13:57:26 +0100] \"GET /index - 200 123"])

        self.logs_dao.create_apache_logs.assert_called_once_with(apache_logs=[ApacheLog(
            ip_address="127.0.0.1",
            date=datetime.strptime("19/Dec/2020:13:57:26+0100", '%d/%b/%Y:%H:%M:%S%z'),
            method="GET",
            uri="/index",
            status_code=200,
            size=123,
        )])

    def test_import_logs_invalid_size(self):
        usecase = ParseLogsUseCase(self.logs_dao, self.request_dao, self.import_status_dao)

        usecase._import_logs(rows=["127.0.0.1 - - [19/Dec/2020:13:57:26 +0100] \"GET /index - 200 qwe"])

        self.logs_dao.create_apache_logs.assert_called_once_with(apache_logs=[ApacheLog(
            ip_address="127.0.0.1",
            date=datetime.strptime("19/Dec/2020:13:57:26+0100", '%d/%b/%Y:%H:%M:%S%z'),
            method="GET",
            uri="/index",
            status_code=200,
            size=0,
        )])


class GetLogsUseCaseTestCase(TestCase):
    def setUp(self) -> None:
        self.dao = mock.Mock()

    def test_execute(self):
        page = mock.Mock()
        per_page = mock.Mock()
        query = mock.Mock()
        usecase = GetLogsUseCase(self.dao)
        unique_ip_count = 100
        top_ip_addresses = [CountIPAddress("ip", 1)]
        http_methods_count = [CountMethod("method", 1)]
        sum_sizes = 200
        self.dao.get_count_unique_ip_addresses.return_value = unique_ip_count
        self.dao.get_top_ip_addresses.return_value = top_ip_addresses
        self.dao.get_http_methods_count.return_value = http_methods_count
        self.dao.get_sum_sizes.return_value = sum_sizes
        logs = [ApacheLog(
            ip_address="ip",
            date=datetime.now(),
            method="GET",
            uri="/index",
            status_code=200,
            size=100,
        )]
        pagination = Pagination(
            has_other_pages=True,
            has_previous=True,
            previous_page_number=1,
            number=2,
            num_pages=10,
            has_next=True,
            next_page_number=3,
            page_range=list(range(10))
        )
        statistics = LogStatistics(
            unique_ip_count=unique_ip_count,
            top_ip_addresses=top_ip_addresses,
            http_methods_count=http_methods_count,
            sum_sizes=sum_sizes,
        )
        self.dao.get_logs.return_value = (logs, pagination)

        result = usecase.execute(query=query, page=page, per_page=per_page)

        self.assertEqual(result, PaginatedLogWithStatistics(
            logs=logs,
            statistics=statistics,
            pagination=pagination,
        ))

        self.dao.get_logs.assert_called_once_with(page=page, query=query, per_page=per_page)
        self.dao.get_count_unique_ip_addresses.assert_called_once_with(query=query)
        self.dao.get_top_ip_addresses.assert_called_once_with(query=query)
        self.dao.get_http_methods_count.assert_called_once_with(query=query)
        self.dao.get_sum_sizes.assert_called_once_with(query=query)


class ImportStatusUseCaseTestCase(TestCase):
    def setUp(self) -> None:
        self.dao = mock.Mock()

    def test_execute(self):
        usecase = ImportStatusUseCase(self.dao)
        import_statuses = mock.Mock()
        self.dao.get_import_statuses.return_value = import_statuses

        result = usecase.execute()

        self.assertEqual(result, import_statuses)
        self.dao.get_import_statuses.assert_called_once_with()

from datetime import datetime
from unittest import TestCase, mock

from django.test import TransactionTestCase

from apache_logs.daos import ApacheLogsDAO, RequestDAO, ImportStatusDAO
from apache_logs.entities import ApacheLog, CountIPAddress, CountMethod, Pagination, ImportStatus
from apache_logs.models import ApacheLogORM, ImportStatusORM


class CreateApacheLogsDAOTestCase(TransactionTestCase):
    def setUp(self) -> None:
        self.dao = ApacheLogsDAO()

    def test_create_apache_logs(self):
        apache_logs = [
            ApacheLog(
                ip_address="127.0.0.1",
                date=datetime.now(),
                method="GET",
                uri="/?q=123",
                status_code=200,
                size=1024,
            ),
            ApacheLog(
                ip_address="127.0.0.1",
                date=datetime.now(),
                method="POST",
                uri="/?q=123",
                status_code=200,
                size=1024,
            ),
        ]

        self.dao.create_apache_logs(apache_logs=apache_logs)

        created_apache_logs_orm = ApacheLogORM.objects.all()
        created_apache_logs = [ApacheLog(
            ip_address=log.ip_address,
            date=log.date,
            method=log.method,
            uri=log.uri,
            status_code=log.status_code,
            size=log.size,
        ) for log in created_apache_logs_orm]

        self.assertEqual(len(created_apache_logs), len(apache_logs))


class ApacheLogsDAOTestCase(TransactionTestCase):
    def setUp(self) -> None:
        self.dao = ApacheLogsDAO()
        self.logs = [
            ApacheLogORM(
                ip_address="127.0.0.1",
                date=datetime.now(),
                method="GET",
                uri="/index",
                status_code=200,
                size=201,
            ),
            ApacheLogORM(
                ip_address="127.0.0.1",
                date=datetime.now(),
                method="POST",
                uri="/index",
                status_code=200,
                size=202,
            ),
            ApacheLogORM(
                ip_address="13.66.139.0",
                date=datetime.now(),
                method="GET",
                uri="/index",
                status_code=200,
                size=203,
            )
        ]
        ApacheLogORM.objects.bulk_create(self.logs)

    def test_count_unique_ip_addresses_without_query(self):
        count = self.dao.get_count_unique_ip_addresses(query="")

        self.assertEqual(count, 2)

    def test_count_unique_ip_addresses_with_query(self):
        count = self.dao.get_count_unique_ip_addresses(query="POST")

        self.assertEqual(count, 1)

    def test_top_ip_addresses_without_query(self):
        top_ip_addresses = self.dao.get_top_ip_addresses(addresses_count=1, query="")

        self.assertEqual(top_ip_addresses, [CountIPAddress(ip_address="127.0.0.1", count=2)])

    def test_top_ip_addresses_with_query(self):
        top_ip_addresses = self.dao.get_top_ip_addresses(addresses_count=1, query="POST")

        self.assertEqual(top_ip_addresses, [CountIPAddress(ip_address="127.0.0.1", count=1)])

    def test_get_http_methods_count_without_query(self):
        count_methods = self.dao.get_http_methods_count(query="")

        test_count_methods = [
            CountMethod(method="GET", count=2),
            CountMethod(method="POST", count=1),
        ]

        self.assertEqual(len(count_methods), len(test_count_methods))

    def test_get_http_methods_count_with_query(self):
        count_methods = self.dao.get_http_methods_count(query="POST")

        self.assertEqual(count_methods, [
            CountMethod(method="POST", count=1),
        ])

    def test_get_sum_sizes_without_query(self):
        sum_sizes = self.dao.get_sum_sizes(query="")

        self.assertEqual(sum_sizes, 201 + 202 + 203)

    def test_get_sum_sizes_with_query(self):
        sum_sizes = self.dao.get_sum_sizes(query="POST")

        self.assertEqual(sum_sizes, 202)

    def test_get_logs(self):
        entity_logs = [
            ApacheLog(
                ip_address=log.ip_address,
                date=log.date,
                method=log.method,
                uri=log.uri,
                status_code=log.status_code,
                size=log.size,
            ) for log in self.logs
        ]
        pagination = Pagination(
            page_range=[1],
            has_other_pages=False,
            has_previous=False,
            previous_page_number=0,
            number=1,
            num_pages=1,
            has_next=False,
            next_page_number=0,
        )

        logs = self.dao.get_logs(page=1, per_page=25, query="")

        self.assertEqual(len(logs[0]), len(entity_logs))
        self.assertEqual(logs[1], pagination)


class RequestDAOTestCase(TestCase):
    def setUp(self) -> None:
        self.dao = RequestDAO()
        self.url = "http://www.almhuette-raith.at/apache-log/access.log"

    @mock.patch("apache_logs.daos.requests")
    def test_check_partial_content_false(self, requests_mock):
        headers_mock = mock.Mock()
        headers_mock.headers = {}
        requests_mock.head.return_value = headers_mock
        result = self.dao.check_partial_content(url=self.url)

        self.assertEqual(result, (False, 0))

        requests_mock.head.assert_called_once_with(self.url)

    @mock.patch("apache_logs.daos.requests")
    def test_check_partial_content_true(self, requests_mock):
        headers_mock = mock.Mock()
        headers_mock.headers = {"Accept-Ranges": True, "Content-Length": 100}
        requests_mock.head.return_value = headers_mock
        result = self.dao.check_partial_content(url=self.url)

        self.assertEqual(result, (True, 100))

        requests_mock.head.assert_called_once_with(self.url)

    @mock.patch("apache_logs.daos.requests")
    def test_get_partial_rows(self, requests_mock):
        from_bytes = 0
        to_bytes = 100
        result_mock = mock.Mock()
        result_mock.content = b"000\n000"
        requests_mock.get.return_value = result_mock
        result = self.dao.get_partial_rows(url=self.url, from_bytes=from_bytes, to_bytes=to_bytes)

        self.assertEqual(result, ["000", "000"])

        requests_mock.get.assert_called_once_with(self.url, headers={"Range": f"bytes={from_bytes}-{to_bytes}"})

    @mock.patch("apache_logs.daos.requests")
    def test_get_full_rows(self, requests_mock):
        result_mock = mock.Mock()
        result_mock.content = b"000\n000"
        requests_mock.get.return_value = result_mock
        result = self.dao.get_full_rows(url=self.url)

        self.assertEqual(result, ["000", "000"])

        requests_mock.get.assert_called_once_with(self.url)


class ImportStatusDAOTestCase(TransactionTestCase):
    def setUp(self) -> None:
        self.dao = ImportStatusDAO()

    def test_create_import_status(self):
        import_status = self.dao.create_import_status()

        import_statuses = ImportStatusORM.objects.all()

        self.assertEqual(len(import_statuses), 1)
        self.assertEqual(import_status, ImportStatus(
            pk=import_statuses[0].pk,
            percent=1,
            status=ImportStatusORM.STATUS_START,
        ))

    def test_update_import_status(self):
        import_status = ImportStatusORM()
        import_status.save()

        updated_import_status = self.dao.update_import_status(import_status_id=import_status.pk, percent=20)

        updated_import_status_orm = ImportStatusORM.objects.get(pk=import_status.pk)

        self.assertEqual(ImportStatus(
            pk=updated_import_status_orm.pk,
            percent=updated_import_status_orm.percent,
            status=updated_import_status_orm.status
        ), updated_import_status)

    def test_finish_import_status(self):
        import_status = ImportStatusORM()
        import_status.save()

        finished_import_status = self.dao.finish_import_status(import_status_id=import_status.pk)

        finished_import_status_orm = ImportStatusORM.objects.get(pk=import_status.pk)

        self.assertEqual(finished_import_status, ImportStatus(
            pk=finished_import_status_orm.pk,
            percent=100,
            status=ImportStatusORM.STATUS_FINISH,
        ))

    def test_get_import_statuses(self):
        import_status = ImportStatusORM()
        import_status.save()

        import_statuses = self.dao.get_import_statuses()

        self.assertEqual(import_statuses, [ImportStatus(
            pk=import_status.pk,
            percent=1,
            status=ImportStatusORM.STATUS_START,
        )])

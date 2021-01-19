from unittest import TestCase, mock

from apache_logs.services import ParseLogsCeleryService


class ServicesTestCase(TestCase):
    @mock.patch("apache_logs.services.parse_logs_task")
    def test_parse_logs_celery_service__valid_url(self, parse_logs_task_mock: mock.Mock):
        parse_logs_celery_service = ParseLogsCeleryService()
        url = "https://url.com"

        parse_logs_celery_service.execute(url=url)

        parse_logs_task_mock.delay.assert_called_once_with(url)

    @mock.patch("apache_logs.services.parse_logs_task")
    def test_parse_logs_celery_service__invalid_url(self, parse_logs_task_mock: mock.Mock):
        parse_logs_celery_service = ParseLogsCeleryService()
        url = "invalid_url"

        with self.assertRaises(ParseLogsCeleryService.ParseLogsCeleryValidationError):
            parse_logs_celery_service.execute(url=url)

            parse_logs_task_mock.delay.assert_not_called()

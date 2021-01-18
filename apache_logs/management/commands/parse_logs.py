from django.core.management.base import BaseCommand

from apache_logs.services import ParseLogsCeleryService


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("url", action="store", type=str)

    def handle(self, url: str, *args, **options):
        parse_logs_celery_service = ParseLogsCeleryService()

        try:
            parse_logs_celery_service.execute(url=url)
        except parse_logs_celery_service.ParseLogsCeleryValidationError:
            print(f"'{url}' is not a valid URL!")

        return

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from apache_logs.tasks import parse_logs_task


class ParseLogsCeleryService:
    class ParseLogsCeleryValidationError(Exception):
        pass

    def execute(self, url):
        url_validator = URLValidator()

        try:
            url_validator(url)
        except ValidationError:
            raise self.ParseLogsCeleryValidationError

        parse_logs_task.delay(url)

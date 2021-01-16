from apache_logs.daos import ApacheLogsDao
from apache_logs.usecases import ParseLogsUseCase
from parsing_logs.celery import celery_app


@celery_app.task
def parse_logs_task(url: str):
    parse_logs_dao = ApacheLogsDao()

    parse_logs_service = ParseLogsUseCase(parse_logs_dao)
    parse_logs_service.execute(url=url)

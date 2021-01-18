from apache_logs.daos import ApacheLogsDAO, RequestDAO, ImportStatusDAO
from apache_logs.usecases import ParseLogsUseCase
from parsing_logs.celery import celery_app


@celery_app.task
def parse_logs_task(url: str):
    parse_logs_dao = ApacheLogsDAO()
    request_dao = RequestDAO()
    import_status_dao = ImportStatusDAO()
    parse_logs_service = ParseLogsUseCase(
        logs_dao=parse_logs_dao,
        request_dao=request_dao,
        import_status_dao=import_status_dao,
    )

    parse_logs_service.execute(url=url)

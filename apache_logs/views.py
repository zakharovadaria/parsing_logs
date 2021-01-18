import dataclasses

from django.http import JsonResponse
from django.shortcuts import render

from apache_logs.daos import ApacheLogsDAO, ImportStatusDAO
from apache_logs.usecases import GetLogsUseCase, ImportStatusUseCase


def index(request):
    dao = ApacheLogsDAO()
    usecase = GetLogsUseCase(logs_dao=dao)

    query = request.GET.get("q", "")
    page = request.GET.get("page", 1)

    paginated_logs_with_statistics = usecase.execute(page=page, query=query)

    context = {
        **dataclasses.asdict(paginated_logs_with_statistics),
    }
    return render(request, 'apache_logs/index.html', context)


def import_status(request):
    dao = ImportStatusDAO()
    usecase = ImportStatusUseCase(dao=dao)

    import_statuses = usecase.execute()

    count_not_finished_import_statuses = len([status for status in import_statuses if status.status == "start"])

    percents = [{"id": import_status.pk, "percent": import_status.percent} for import_status in import_statuses]
    return JsonResponse({"percents": percents, "logs_import": bool(count_not_finished_import_statuses)})

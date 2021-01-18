import dataclasses

from django.shortcuts import render

from apache_logs.daos import ApacheLogsDao
from apache_logs.usecases import GetLogsUseCase

dao = ApacheLogsDao()
usecase = GetLogsUseCase(logs_dao=dao)


def index(request):
    query = request.GET.get("q", "")
    page = request.GET.get("page", 1)

    paginated_logs_with_statistics = usecase.execute(page=page, query=query)

    context = {
        **dataclasses.asdict(paginated_logs_with_statistics),
    }
    return render(request, 'apache_logs/index.html', context)


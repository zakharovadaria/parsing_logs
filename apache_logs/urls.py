from django.urls import path

from apache_logs.views import index, import_status

urlpatterns = [
    path("import_status", import_status, name="import_status"),
    path("", index, name="index"),
]

from django.urls import path

from apache_logs.views import index

urlpatterns = [
    path("", index, name='index'),
]

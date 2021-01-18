from django.db import models


class ApacheLogORM(models.Model):
    ip_address = models.GenericIPAddressField()
    date = models.DateTimeField()
    method = models.CharField(max_length=10)
    uri = models.TextField()
    status_code = models.IntegerField()
    size = models.IntegerField()

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class ApacheLogORM(models.Model):
    ip_address = models.GenericIPAddressField()
    date = models.DateTimeField()
    method = models.CharField(max_length=10)
    uri = models.TextField()
    status_code = models.IntegerField()
    size = models.IntegerField()


class ImportStatusORM(models.Model):
    STATUS_START = "start"
    STATUS_FINISH = "finish"

    STATUS_CHOICES = [
        (STATUS_START, "Start"),
        (STATUS_FINISH, "Finish"),
    ]

    percent = models.IntegerField(default=1, validators=[
        MaxValueValidator(100),
        MinValueValidator(1),
    ])
    status = models.CharField(choices=STATUS_CHOICES, max_length=8, default=STATUS_START)

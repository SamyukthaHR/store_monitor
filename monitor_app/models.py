import datetime

from django.db import models


class StoreStatus(models.Model):
    store_id = models.CharField(max_length=50)
    status = models.CharField(max_length=10)
    timestamp_utc = models.DateTimeField()


class StoreTimezone(models.Model):
    store_id = models.CharField(max_length=50)
    timezone_str = models.CharField(max_length=50)


class StoreMenuHours(models.Model):
    store_id = models.CharField(max_length=50)
    day = models.IntegerField()
    start_time_local = models.TimeField()
    end_time_local = models.TimeField()


class ReportDetails(models.Model):
    report_id = models.CharField(max_length=10)
    report_url = models.TextField()
    status = models.CharField(max_length=20)
    err_msg = models.CharField(max_length=50)
    created_at = models.DateTimeField(default=datetime.datetime.now())
    updated_at = models.DateTimeField(default=datetime.datetime.now())


class AppConstants(models.Model):
    key = models.CharField(max_length=30)
    value = models.CharField(max_length=40)
    is_deleted = models.BooleanField(default=False)

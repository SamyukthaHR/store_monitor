from rest_framework import serializers

from monitor_app.models import StoreStatus, StoreTimezone, StoreMenuHours, ReportDetails, AppConstants


class StoreStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreStatus
        fields = ['store_id', 'status', 'timestamp_utc']

    store_id = serializers.CharField()
    status = serializers.CharField()
    timestamp_utc = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S.%f%z')


class StoreTimezoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreTimezone
        fields = ['store_id', 'timezone_str']


class StoreMenuHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreMenuHours
        fields = ['store_id', 'day', 'start_time_local', 'end_time_local']


class ReportDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportDetails
        fields = ['report_id', 'report_url', 'status', 'err_msg']

    report_id = serializers.CharField()
    report_url = serializers.CharField()
    status = serializers.CharField()
    err_msg = serializers.CharField()


class AppConstantsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppConstants
        fields = ['key', 'value']

    key = serializers.CharField()
    value = serializers.CharField()

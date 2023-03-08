import datetime
import json
import random
import string

from django.views import View

from monitor_app.models import ReportDetails
from monitor_app.serializer import ReportDetailsSerializer
from monitor_app.tasks import trigger_report
from utils.constants import HttpStatusCode, HttpErrorMsg
from utils.http_response import send_http_response
from utils.util import format_report_response, format_serializer_data


class TriggerReportView(View):
    def post(self, request, *args, **kwargs):
        print(request.body, json.loads(request.body))
        body = json.loads(request.body)
        report_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        created_at = updated_at = datetime.datetime.now(datetime.timezone.utc)
        report = ReportDetails(report_id=report_id, status='initiated', created_at=created_at, updated_at=updated_at)
        report.save()
        trigger_report.delay(body, report_id)
        data = {
            "report_id": report_id
        }
        return send_http_response(data=data, status=HttpStatusCode['SUCCESS'])


class GetReportView(View):
    def get(self, request, *args, **kwargs):
        print(request, request.GET.get('report_id'))
        report_id = request.GET.get('report_id')
        try:
            report_qs = ReportDetails.objects.filter(report_id=report_id)
            serializer = ReportDetailsSerializer(report_qs, many=True)
            data = format_serializer_data(serializer.data)
            if data:
                data = format_report_response(data)
            return send_http_response(data=data)
        except Exception as e:
            return send_http_response(status=HttpStatusCode['SERVER_ERROR'], err_msg=HttpErrorMsg['SERVER_ERROR'])

from django.urls import path

from monitor_app.views import TriggerReportView, GetReportView


urlpatterns = [
    path('trigger_report', TriggerReportView.as_view()),
    path('get_report', GetReportView.as_view())
]
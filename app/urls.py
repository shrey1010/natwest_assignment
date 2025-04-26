from django.urls import path
from .views import GenerateReportView, UploadRulesView, DownloadReportView, TriggerScheduleReportView

urlpatterns = [
    path('generate-report/', GenerateReportView.as_view(), name='generate-report'),
    path('upload-rules/', UploadRulesView.as_view(), name='upload_rules'),
    path('download-report/<str:task_id>/', DownloadReportView.as_view(), name='download-report'),
    path('trigger-scheduled-report/', TriggerScheduleReportView.as_view(), name='trigger_scheduled_report'),
]

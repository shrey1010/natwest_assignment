from django.db import models
import uuid

class ReportRun(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report_name = models.CharField(max_length=255)
    task_id = models.CharField(max_length=255)
    output_path = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=50, default="Scheduled") 

    def __str__(self):
        return self.report_name

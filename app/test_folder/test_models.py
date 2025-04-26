from django.test import TestCase
from app.models import ReportRun
import uuid

class ReportRunModelTest(TestCase):
    
    def setUp(self):
        self.test_uuid = uuid.uuid4()
        self.report_name = "Test Report"
        self.task_id = "celery-task-id-123"
        self.output_path = "/tmp/test_output.csv"
        self.status = "Scheduled"

        self.report_run = ReportRun.objects.create(
            id=self.test_uuid,
            report_name=self.report_name,
            task_id=self.task_id,
            output_path=self.output_path,
            status=self.status
        )

    def test_report_run_creation(self):
        self.assertIsInstance(self.report_run, ReportRun)
        self.assertEqual(self.report_run.report_name, self.report_name)
        self.assertEqual(self.report_run.task_id, self.task_id)
        self.assertEqual(self.report_run.output_path, self.output_path)
        self.assertEqual(self.report_run.status, self.status)

    def test_report_run_str_method(self):
        self.assertEqual(str(self.report_run), self.report_name)

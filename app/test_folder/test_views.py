from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch
from users.models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken
import tempfile
from unittest.mock import patch, MagicMock
import os


class ReportGenerationTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(email="test@example.com", password="testpass123", name="Test User")
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        self.input_file = SimpleUploadedFile("input.csv", b"id,value\n1,10\n2,20", content_type="text/csv")
        self.reference_file = SimpleUploadedFile("reference.csv", b"refkey1,refdata1\n1,Data1\n2,Data2", content_type="text/csv")
        self.rules_file = SimpleUploadedFile("rules.json", b"[{\"output\": \"sum\", \"formula\": \"value + 1\"}]", content_type="application/json")


    @patch("builtins.open", side_effect=Exception("File save error"))
    def test_upload_rules_exception_handling(self, mock_open):
        url = reverse("upload_rules") + "?type=json"
        valid_file = SimpleUploadedFile("rules.json", b'[{"output": "sum", "formula": "value + 1"}]', content_type="application/json")
        
        response = self.client.post(url, data={'file': valid_file}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error", response.data)
        self.assertEqual(response.data['error'], "File save error")
        
    def test_upload_rules_invalid_file_type(self):
        invalid_file = SimpleUploadedFile("rules.csv", b"some,invalid,data", content_type="text/csv")
        url = reverse("upload_rules") + "?type=csv"
        
        response = self.client.post(url, data={'file': invalid_file}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Unsupported file type. Use 'json' or 'yaml'.")
        
    def test_upload_rules_no_file(self):
        url = reverse("upload_rules") + "?type=json"
        
        response = self.client.post(url, data={}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "No file uploaded.")
        
    def test_generate_report_missing_files(self):
        url = reverse('generate-report')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], "Both input and reference files are required.")

    def test_generate_report(self):
        url = reverse("generate-report")
        response = self.client.post(url, data={
            'input': self.input_file,
            'reference': self.reference_file
        }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn("task_id", response.data)

    def test_upload_rules(self):
        url = reverse("upload_rules") + "?type=json"
        response = self.client.post(url, data={
            'file': self.rules_file
        }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)

    def test_trigger_scheduled_report(self):
        url = reverse("trigger_scheduled_report")
        response = self.client.post(url, data={
            "cron": "*/5 * * * *",
            "input_file": self.input_file,
            "reference_file": self.reference_file,
            "rules_file": self.rules_file,
            "report_name": "Test Report"
        }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("message", response.data)
        self.assertIn("task_id", response.data)

    def test_download_report_pending(self):
        url = reverse("download-report", args=["fake-task-id"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn("status", response.data)
        
    @patch("os.path.exists", return_value=False)
    @patch("app.views.AsyncResult")
    def test_download_report_file_not_found(self, mock_async_result, mock_exists):
        mock_result = MagicMock()
        mock_result.ready.return_value = True
        mock_result.get.return_value = "/fake/path/report.csv"
        mock_async_result.return_value = mock_result

        url = reverse("download-report", args=["fake-task-id"])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], "Report file not found.")


    @patch("os.path.exists", return_value=True)
    @patch("builtins.open", new_callable=MagicMock)
    @patch("app.views.AsyncResult")
    def test_download_report_success(self, mock_async_result, mock_open, mock_exists):
        output_path = "/path/to/fake-report.csv"

        mock_result = MagicMock()
        mock_result.ready.return_value = True
        mock_result.get.return_value = output_path
        mock_async_result.return_value = mock_result

        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        url = reverse("download-report", args=["fake-task-id"])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertEqual(response['Content-Disposition'], f'attachment; filename="{os.path.basename(output_path)}"')
        
class TriggerScheduleReportViewTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(email="testuser@example.com", password="testpass123", name="Test User")
        self.client.force_authenticate(user=self.user)

        self.url = reverse("trigger_scheduled_report")
        self.valid_cron = "*/5 * * * *"
        self.file_data = {
            "input_file": SimpleUploadedFile("input.csv", b"data1,data2\n1,2"),
            "reference_file": SimpleUploadedFile("ref.csv", b"refkey1,refkey2,refdata1,refdata2,refdata3,refdata4\nA,B,x,y,z,1"),
            "rules_file": SimpleUploadedFile("rules.json", b'[{"output": "result", "formula": "data1 + data2"}]')
        }

    def test_missing_required_fields(self):
        response = self.client.post(self.url, data=self.file_data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_invalid_cron_expression(self):
        data = {"cron": "invalid_cron", **self.file_data}
        response = self.client.post(self.url, data=data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid cron format", response.data["error"])

    @patch("app.views.generate_report_task.delay")
    @patch("app.views.CrontabSchedule.objects.get_or_create")
    @patch("app.views.PeriodicTask.objects.create")
    def test_generic_exception_handling(self, mock_create, mock_cron, mock_task):
        mock_cron.side_effect = Exception("Unexpected error!")
        data = {"cron": self.valid_cron, **self.file_data}
        response = self.client.post(self.url, data=data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error", response.data)

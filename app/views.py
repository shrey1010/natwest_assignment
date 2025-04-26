import os
import uuid
import json
import yaml

from django.conf import settings
from django.http import FileResponse
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from celery.result import AsyncResult
from django_celery_beat.models import PeriodicTask, CrontabSchedule

from .utils import generate_report_task
from .models import ReportRun




class GenerateReportView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        input_file = request.FILES.get('input')
        reference_file = request.FILES.get('reference')

        if not input_file or not reference_file:
            return Response({"error": "Both input and reference files are required."}, status=400)

        unique_id = str(uuid.uuid4())
        input_path = os.path.join(settings.MEDIA_ROOT, f"{unique_id}_input.csv")
        ref_path = os.path.join(settings.MEDIA_ROOT, f"{unique_id}_reference.csv")
        rules_path = os.path.join(settings.BASE_DIR, 'app', 'transformation', 'configs', 'rules.json')

        for file_obj, path in [(input_file, input_path), (reference_file, ref_path)]:
            with open(path, 'wb') as f:
                for chunk in file_obj.chunks():
                    f.write(chunk)

        task = generate_report_task.delay(input_path, ref_path, rules_path)
        return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)


class DownloadReportView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, task_id):
        result = AsyncResult(task_id)
        if result.ready():
            output_path = result.get()

            if not os.path.exists(output_path):
                return Response({"error": "Report file not found."}, status=404)

            return FileResponse(
                open(output_path, 'rb'),
                content_type='text/csv',
                as_attachment=True,
                filename=os.path.basename(output_path)
            )

        return Response({"status": result.status}, status=status.HTTP_202_ACCEPTED)


class UploadRulesView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file_type = request.query_params.get('type', 'json').lower()
        uploaded_file = request.FILES.get('file')

        if file_type not in ['json', 'yaml']:
            return Response({"error": "Unsupported file type. Use 'json' or 'yaml'."}, status=400)

        if not uploaded_file:
            return Response({"error": "No file uploaded."}, status=400)

        rules_dir = os.path.join(settings.BASE_DIR, 'app', 'transformation', 'configs')
        os.makedirs(rules_dir, exist_ok=True)
        rules_path = os.path.join(rules_dir, f"rules.{file_type}")

        try:
            with open(rules_path, 'wb') as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)
            return Response({"message": f"Rules file uploaded successfully as rules.{file_type}"}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class TriggerScheduleReportView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cron = request.data.get("cron")
        input_file = request.FILES.get("input_file")
        reference_file = request.FILES.get("reference_file")
        rules_file = request.FILES.get("rules_file")
        report_name = request.data.get("report_name") or f"report_{uuid.uuid4().hex[:6]}"

        if not all([cron, input_file, reference_file, rules_file]):
            return Response(
                {"error": "cron, input_file, reference_file, and rules_file are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            parts = cron.strip().split()
            if len(parts) != 5:
                raise ValueError("Invalid cron format. Use format like '*/5 * * * *'.")

            minute, hour, day_of_month, month_of_year, day_of_week = parts

            schedule, _ = CrontabSchedule.objects.get_or_create(
                minute=minute,
                hour=hour,
                day_of_month=day_of_month,
                month_of_year=month_of_year,
                day_of_week=day_of_week,
            )

            unique_id = uuid.uuid4().hex
            input_path = os.path.join(settings.MEDIA_ROOT, f"{unique_id}_input.csv")
            ref_path = os.path.join(settings.MEDIA_ROOT, f"{unique_id}_reference.csv")
            rules_path = os.path.join(settings.BASE_DIR, 'app', 'transformation', 'configs', f"{unique_id}_rules.json")

            for file_obj, path in [
                (input_file, input_path),
                (reference_file, ref_path),
                (rules_file, rules_path),
            ]:
                with open(path, 'wb') as f:
                    for chunk in file_obj.chunks():
                        f.write(chunk)

            task = generate_report_task.delay(input_path, ref_path, rules_path)

            PeriodicTask.objects.create(
                crontab=schedule,
                name=f"{report_name}_{unique_id[:6]}",
                task='app.utils.generate_report_task',
                args=json.dumps([input_path, ref_path, rules_path])
            )

            return Response({
                "message": "Scheduled report generation task created.",
                "task_id": task.id,
                "report_name": report_name,
                "cron": cron
            }, status=status.HTTP_201_CREATED)

        except ValueError as ve:
            return Response({"error": str(ve)}, status=400)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
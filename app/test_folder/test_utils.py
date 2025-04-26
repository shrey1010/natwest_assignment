import os
import tempfile
import uuid
import json
import pandas as pd

from django.test import TestCase
from app.utils import generate_report_task


class GenerateReportTaskTest(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        uid = uuid.uuid4().hex

        self.input_path = os.path.join(self.temp_dir, f"{uid}_input.csv")
        self.ref_path = os.path.join(self.temp_dir, f"{uid}_reference.csv")
        self.rules_path = os.path.join(self.temp_dir, "rules.json")
        self.output_path = self.input_path.replace("input.csv", "output.csv")

        with open(self.input_path, "w") as f:
            f.write("data1,data2,refkey1,refkey2\n10,20,R1,R2")

        with open(self.ref_path, "w") as f:
            f.write("refkey1,refkey2,refdata1,refdata2,refdata3,refdata4\nR1,R2,X,Y,Z,99")

        rules = [{"output": "sum", "formula": "data1 + data2"}]
        with open(self.rules_path, "w") as f:
            json.dump(rules, f)

    def test_generate_report_creates_output_file(self):
        result_path = generate_report_task(self.input_path, self.ref_path, self.rules_path)
        
        self.assertTrue(os.path.exists(result_path))

        df = pd.read_csv(result_path)
        self.assertIn("sum", df.columns)
        self.assertEqual(df["sum"][0], 30) 

    def tearDown(self):
        for file_path in [self.input_path, self.ref_path, self.rules_path, self.output_path]:
            if os.path.exists(file_path):
                os.remove(file_path)
        os.rmdir(self.temp_dir)

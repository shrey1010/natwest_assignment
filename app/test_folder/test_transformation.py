import os
import json
import yaml
import tempfile
import pandas as pd
from django.test import TestCase
from app.transformation import TransformationEngine


class TransformationEngineTest(TestCase):
    def setUp(self):
        self.rules = [
            {"output": "outfield1", "formula": "field1 + field2"},
            {"output": "outfield2", "formula": "refdata1"},
            {"output": "outfield3", "formula": "refdata2 + refdata3"},
            {"output": "outfield4", "formula": "field3 * max(field5, refdata4)"},
            {"output": "outfield5", "formula": "max(field5, refdata4)"}
        ]
        self.temp_dir = tempfile.TemporaryDirectory()
        self.rules_json_path = os.path.join(self.temp_dir.name, 'rules.json')
        self.rules_yaml_path = os.path.join(self.temp_dir.name, 'rules.yaml')
        self.rules_txt_path = os.path.join(self.temp_dir.name, 'rules.txt')
        
        with open(self.rules_json_path, 'w') as f:
            json.dump(self.rules, f)

        with open(self.rules_yaml_path, 'w') as f:
            yaml.safe_dump(self.rules, f)

        with open(self.rules_txt_path, 'w') as f:
            f.write("invalid content")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_load_json_rules(self):
        engine = TransformationEngine(self.rules_json_path)
        self.assertEqual(engine.rules, self.rules)

    def test_load_yaml_rules(self):
        engine = TransformationEngine(self.rules_yaml_path)
        self.assertEqual(engine.rules, self.rules)

    def test_invalid_file_format(self):
        with self.assertRaises(ValueError) as ctx:
            TransformationEngine(self.rules_txt_path)
        self.assertIn("Unsupported rule file format", str(ctx.exception))

    def test_eval_exception_handling(self):
        faulty_rules = [{"output": "bad_formula", "formula": "fieldX + refY"}]
        faulty_path = os.path.join(self.temp_dir.name, 'faulty.json')
        with open(faulty_path, 'w') as f:
            json.dump(faulty_rules, f)

        engine = TransformationEngine(faulty_path)
        row = engine.apply_rules({"field1": "A"}, {"refdata1": "B"})
        self.assertIn("ERROR in", row["bad_formula"])

    def test_value_error_handling_in_float_cast(self):
        engine = TransformationEngine(self.rules_json_path)
        row = engine.apply_rules(
            {"field3": "not_a_number", "field5": "10", "field1": "x", "field2": "y"},
            {"refdata1": "A", "refdata2": "B", "refdata3": "C", "refdata4": "20"}
        )
        self.assertIn("outfield1", row)

    def test_process_dataframe_overwrites_file(self):
        input_path = os.path.join(self.temp_dir.name, 'input.csv')
        ref_path = os.path.join(self.temp_dir.name, 'reference.csv')
        output_path = os.path.join(self.temp_dir.name, 'output.csv')

        pd.DataFrame([{
            "field1": "A", "field2": "B", "field3": "5", "field4": "X",
            "field5": "10", "refkey1": "k1", "refkey2": "k2"
        }]).to_csv(input_path, index=False)

        pd.DataFrame([{
            "refkey1": "k1", "refdata1": "D", "refkey2": "k2",
            "refdata2": "E", "refdata3": "F", "refdata4": 99
        }]).to_csv(ref_path, index=False)

        with open(output_path, 'w') as f:
            f.write("old data")

        engine = TransformationEngine(self.rules_json_path)
        engine.process_dataframe(input_path, ref_path, output_path)

        with open(output_path, 'r') as f:
            content = f.read()
            self.assertNotIn("old data", content) 

    def test_missing_ref_fields_get_default_values(self):
        engine = TransformationEngine(self.rules_json_path)
        row = engine.apply_rules(
            {
                "field1": "A", "field2": "B", "field3": "1", "field5": "2",
            },
            {} 
        )
        self.assertTrue(row["outfield2"].startswith("ERROR in 'refdata1'"))
        self.assertIn("name 'refdata1' is not defined", row["outfield2"])

        
    def test_large_file_processing_with_chunks(self):
        input_path = os.path.join(self.temp_dir.name, 'large_input.csv')
        ref_path = os.path.join(self.temp_dir.name, 'large_reference.csv')
        output_path = os.path.join(self.temp_dir.name, 'large_output.csv')

        input_data = [{
            "field1": f"A{i}",
            "field2": f"B{i}",
            "field3": str(i),
            "field4": "X",
            "field5": str(i * 1.1),
            "refkey1": "k1",
            "refkey2": "k2"
        } for i in range(25000)]

        ref_data = [{
            "refkey1": "k1", "refdata1": "D", "refkey2": "k2",
            "refdata2": "E", "refdata3": "F", "refdata4": 42
        }]

        pd.DataFrame(input_data).to_csv(input_path, index=False)
        pd.DataFrame(ref_data).to_csv(ref_path, index=False)

        engine = TransformationEngine(self.rules_json_path)
        engine.process_dataframe(input_path, ref_path, output_path)

        output_df = pd.read_csv(output_path)
        self.assertEqual(len(output_df), 25000)
        self.assertIn("outfield1", output_df.columns)
        self.assertIn("outfield5", output_df.columns)
        
    def test_default_values_for_missing_reference_fields(self):
        input_data = pd.DataFrame([{
            "field1": "A", "field2": "B", "field3": "3", "field4": "D", "field5": "5.5",
            "refkey1": "missing1", "refkey2": "missing2"
        }])
        
        ref_data_headers = ["refkey1", "refdata1", "refkey2", "refdata2", "refdata3", "refdata4"]

        input_path = os.path.join(self.temp_dir.name, "input.csv")
        ref_path = os.path.join(self.temp_dir.name, "reference.csv")
        rules_path = os.path.join(self.temp_dir.name, "rules.json")
        output_path = os.path.join(self.temp_dir.name, "output.csv")

        input_data.to_csv(input_path, index=False)
        pd.DataFrame(columns=ref_data_headers).to_csv(ref_path, index=False)

        rules = [
            {"output": "outfield1", "formula": "field1 + field2"},            
            {"output": "outfield2", "formula": "refdata1"},                  
            {"output": "outfield3", "formula": "refdata2 + refdata3"},     
            {"output": "outfield4", "formula": "field3 * max(field5, refdata4)"}, 
            {"output": "outfield5", "formula": "max(field5, refdata4)"}   
        ]
        with open(rules_path, "w") as f:
            json.dump(rules, f)

        engine = TransformationEngine(rules_path)
        engine.process_dataframe(input_path, ref_path, output_path)

        df = pd.read_csv(output_path)

        self.assertEqual(df.shape[0], 1)
        row = df.iloc[0].to_dict()

        self.assertEqual(row["outfield2"], "MISSING_refdata1")
        self.assertEqual(row["outfield3"], "MISSING_refdata2MISSING_refdata3")

        self.assertAlmostEqual(float(row["outfield4"]), float(3) * max(5.5, 0))
        self.assertAlmostEqual(float(row["outfield5"]), max(5.5, 0))

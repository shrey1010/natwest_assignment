import json
import yaml
from typing import Dict, List
import pandas as pd
import os

class TransformationEngine:
    def __init__(self, rules_path: str):
        self.rules = self._load_rules(rules_path)

    def _load_rules(self, path: str) -> List[Dict]:
        if path.endswith('.json'):
            with open(path, 'r') as f:
                return json.load(f)
        elif path.endswith('.yaml') or path.endswith('.yml'):
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        else:
            raise ValueError("Unsupported rule file format. Use .json or .yaml")

    def apply_rules(self, input_row: Dict, reference_row: Dict) -> Dict:
        output_row = {}
        allowed_functions = {"max": max, "min": min, "abs": abs, "round": round}

        context = {**input_row, **reference_row, **allowed_functions}
        
        for key, value in context.items():
            if  isinstance(value, str):
                try:
                    context[key] = float(value)
                except (ValueError, TypeError):
                    pass

        for rule in self.rules:
            output_field = rule["output"]
            formula = rule["formula"]

            try:
                output_row[output_field] = eval(formula, {}, context)
            except Exception as e:
                involved_values = {k: context.get(k) for k in context if k in formula}
                output_row[output_field] = (
                    f"ERROR in '{formula}': {str(e)} | Values: {involved_values}"
                )

        return output_row



    def process_dataframe(self, input_path: str, ref_path: str, output_path: str):
        ref_df = pd.read_csv(ref_path)
        ref_dict1 = ref_df.set_index('refkey1').to_dict(orient='index')
        ref_dict2 = ref_df.set_index('refkey2').to_dict(orient='index')

        all_ref_fields = {'refdata1', 'refdata2', 'refdata3', 'refdata4'}

        if os.path.exists(output_path):
            os.remove(output_path)

        reader = pd.read_csv(input_path, chunksize=10000)
        is_first_chunk = True

        for chunk in reader:
            output_data = []
            for _, row in chunk.iterrows():
                input_row = row.to_dict()
                ref_row = {}

                ref1_data = ref_dict1.get(input_row.get("refkey1"), {})
                ref2_data = ref_dict2.get(input_row.get("refkey2"), {})
                ref_row.update(ref1_data)
                ref_row.update(ref2_data)

                for field in all_ref_fields:
                    if field not in ref_row:
                        ref_row[field] = 0 if field == "refdata4" else f"MISSING_{field}"

                output_row = self.apply_rules(input_row, ref_row)
                output_data.append(output_row)

            pd.DataFrame(output_data).to_csv(output_path, index=False, mode='a', header=is_first_chunk)
            is_first_chunk = False

# utils.py
from celery import shared_task
import pandas as pd
from io import BytesIO
from .transformation import TransformationEngine

@shared_task
def generate_report_task(input_path, ref_path, rule_path):
    output_path = input_path.replace("input.csv", "output.csv")
    print("output_path", output_path)
    engine = TransformationEngine(rule_path)
    
    engine.process_dataframe(input_path, ref_path, output_path)

    return output_path 


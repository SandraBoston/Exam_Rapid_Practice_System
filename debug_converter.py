#!/usr/bin/env python3
"""
Debug converter output format
"""
import sys
sys.path.append('src')

from converters_2_Evaluate.robust_exam_converter_documented import RobustExamConverter
from pathlib import Path

converter = RobustExamConverter()
exam_dir = Path("Exam_HTML_Raw_Data")

# Test with one file
test_file = exam_dir / "sample_exam.html"
print(f"Testing file: {test_file}")

# Extract data
data = converter.extract_data_from_html(test_file)
print(f"Data keys: {data.keys()}")
print(f"Questions count: {len(data['questions'])}")

# Look at first question structure
if data['questions']:
    first_q = data['questions'][0]
    print(f"First question keys: {first_q.keys()}")
    print(f"First question data:")
    for key, value in first_q.items():
        if isinstance(value, str) and len(value) > 100:
            print(f"  {key}: {value[:100]}...")
        else:
            print(f"  {key}: {value}")

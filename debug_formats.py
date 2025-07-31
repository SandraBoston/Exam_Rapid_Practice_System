#!/usr/bin/env python3
"""
Debug different file formats
"""
import sys
sys.path.append('src')

from converters_2_Evaluate.robust_exam_converter_documented import RobustExamConverter
from pathlib import Path

converter = RobustExamConverter()
exam_dir = Path("Exam_HTML_Raw_Data")

# Test files with issues
test_files = [
    "PE1 -- Module 1 Quiz_20250610_v1.html",
    "PCEP_Exam_Module_3_raw_data.json"
]

for filename in test_files:
    test_file = exam_dir / filename
    print(f"\n{'='*60}")
    print(f"Testing file: {test_file}")
    
    # Extract data
    try:
        if test_file.suffix.lower() == '.html':
            data = converter.extract_data_from_html(test_file)
        elif test_file.suffix.lower() == '.json':
            data = converter.extract_data_from_json(test_file)
        
        if data and 'questions' in data:
            print(f"Questions count: {len(data['questions'])}")
            
            # Look at first question structure
            if data['questions']:
                first_q = data['questions'][0]
                print(f"First question keys: {list(first_q.keys())}")
                print(f"First question sample:")
                for key, value in first_q.items():
                    if isinstance(value, str) and len(value) > 100:
                        print(f"  {key}: {value[:100]}...")
                    elif isinstance(value, list) and len(value) > 4:
                        print(f"  {key}: {value[:4]}... (total: {len(value)} items)")
                    else:
                        print(f"  {key}: {value}")
        else:
            print("No data extracted or no questions found")
            
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        import traceback
        traceback.print_exc()

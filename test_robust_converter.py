#!/usr/bin/env python3
"""
Test Script for Robust Exam Converter (Documented Version)
===========================================================

This script demonstrates how to use the RobustExamConverter to:
1. Test multi-answer detection
2. Process individual files
3. Validate converter functionality

Usage:
    python test_robust_converter.py

Author: AI Assistant
Date: 2025-07-30
"""

import sys
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, 'src')
sys.path.insert(0, 'src/converters_2_Evaluate')

# Test data for demonstration
SAMPLE_QUESTIONS = [
    {
        "question": "Which of the following are Python keywords? (Select two answers)",
        "options": ["def", "class", "hello", "world"],
        "expected_type": "multi-select",
        "expected_count": 2
    },
    {
        "question": "What is the output of print('Hello World')?",
        "options": ["Hello World", "hello world", "HELLO WORLD", "Error"],
        "expected_type": "single-select",
        "expected_count": 1
    },
    {
        "question": "Mark all that apply: Which are valid Python data types?",
        "options": ["int", "str", "list", "array"],
        "expected_type": "multi-select",
        "expected_count": 4
    },
    {
        "question": "Which statements are correct about Python variables?",
        "options": [
            "Variables must be declared",
            "Variables are dynamically typed",
            "Variable names are case-sensitive",
            "Variables cannot contain numbers"
        ],
        "expected_type": "multi-select", 
        "expected_count": 2
    }
]

def test_multi_answer_detection():
    """Test the multi-answer detection functionality"""
    print("🧪 Testing Multi-Answer Detection")
    print("=" * 50)
    
    try:
        # Import from the converters subdirectory
        sys.path.insert(0, 'src/converters_2_Evaluate')
        from robust_exam_converter_documented import RobustExamConverter
        converter = RobustExamConverter()
        
        for i, test_case in enumerate(SAMPLE_QUESTIONS, 1):
            print(f"\nTest {i}: {test_case['question'][:60]}...")
            
            result = converter.detect_multi_answer_requirement(
                test_case['question'], 
                test_case['options']
            )
            
            # Check if detection matches expectations
            type_correct = result['type'] == test_case['expected_type']
            count_reasonable = (
                result['required_answers'] == test_case['expected_count'] or
                (test_case['expected_type'] == 'multi-select' and result['required_answers'] >= 2)
            )
            
            status = "✅" if type_correct and count_reasonable else "❌"
            
            print(f"  {status} Detected: {result['type']} ({result['required_answers']} answers)")
            print(f"     Expected: {test_case['expected_type']} ({test_case['expected_count']} answers)")
            print(f"     Confidence: {result['confidence']:.2f}")
            print(f"     Method: {result['detection_method']}")
            
            if not type_correct:
                print(f"     ⚠️  Type mismatch!")
        
        print(f"\n✅ Multi-answer detection test completed")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure robust_exam_converter_documented.py is in the correct location")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def test_format_detection():
    """Test file format detection"""
    print("\n🔍 Testing Format Detection")
    print("=" * 50)
    
    try:
        # Import from the converters subdirectory
        sys.path.insert(0, 'src/converters_2_Evaluate')
        from robust_exam_converter_documented import RobustExamConverter
        converter = RobustExamConverter()
        
        # Create sample files for testing
        test_files = {
            "test_exam.json": {
                "content": '{"questions": [{"id": 1, "question": "Test?", "options": ["A", "B"]}]}',
                "expected": "json"
            },
            "test_exam.html": {
                "content": '<html><script>let data = {"questions": []};</script></html>',
                "expected": "html"
            }
        }
        
        for filename, test_data in test_files.items():
            # Create temporary test file
            with open(filename, 'w') as f:
                f.write(test_data['content'])
            
            # Test detection
            detected = converter.detect_file_format(filename)
            status = "✅" if detected == test_data['expected'] else "❌"
            
            print(f"  {status} {filename}: detected as {detected} (expected {test_data['expected']})")
            
            # Clean up
            Path(filename).unlink()
        
        print("✅ Format detection test completed")
        
    except Exception as e:
        print(f"❌ Format detection test failed: {e}")

def create_sample_exam_files():
    """Create sample exam files for testing"""
    print("\n📝 Creating Sample Exam Files")
    print("=" * 50)
    
    # Sample JSON exam
    json_exam = {
        "timeLimitInMinutes": 30,
        "questions": [
            {
                "id": 1,
                "question": "What is Python?",
                "options": ["A programming language", "A snake", "A tool", "A framework"],
                "correct": 0,
                "explanation": "Python is a high-level programming language."
            },
            {
                "id": 2,
                "question": "Which of the following are Python data types? (Select two answers)",
                "options": ["int", "str", "array", "pointer"],
                "correct": [0, 1],
                "explanation": "int and str are built-in Python data types."
            }
        ]
    }
    
    # Sample HTML exam
    html_exam = """<!DOCTYPE html>
<html>
<head>
    <title>Sample PCEP Exam</title>
</head>
<body>
    <h1>PCEP Practice Questions</h1>
    
    <script>
    let data = {
        "timeLimitInMinutes": 45,
        "questions": [
            {
                "id": 3,
                "question": "What does the print() function do?",
                "options": ["Displays output", "Calculates values", "Stores data", "Imports modules"],
                "correct": 0,
                "explanation": "The print() function displays output to the console."
            },
            {
                "id": 4,
                "question": "Mark all that apply: Which are valid Python operators?",
                "options": ["+", "-", "*", "&"],
                "correct": [0, 1, 2],
                "explanation": "+, -, and * are arithmetic operators. & is a bitwise operator."
            }
        ]
    };
    </script>
</body>
</html>"""
    
    # Create directories if they don't exist
    Path("Exam_Raw_Data_JSON").mkdir(exist_ok=True)
    Path("Exam_HTML_Raw_Data").mkdir(exist_ok=True)
    
    # Write sample files
    json_file = Path("Exam_Raw_Data_JSON/sample_exam.json")
    html_file = Path("Exam_HTML_Raw_Data/sample_exam.html")
    
    with open(json_file, 'w') as f:
        json.dump(json_exam, f, indent=2)
    
    with open(html_file, 'w') as f:
        f.write(html_exam)
    
    print(f"✅ Created sample JSON file: {json_file}")
    print(f"✅ Created sample HTML file: {html_file}")
    print(f"\nSample files contain:")
    print(f"  - JSON: {len(json_exam['questions'])} questions")
    print(f"  - HTML: 2 questions (embedded in JavaScript)")
    print(f"\nYou can now test the converter with these files!")

def test_data_extraction():
    """Test data extraction from sample files"""
    print("\n📤 Testing Data Extraction")
    print("=" * 50)
    
    try:
        # Import from the converters subdirectory
        sys.path.insert(0, 'src/converters_2_Evaluate')
        from robust_exam_converter_documented import RobustExamConverter
        converter = RobustExamConverter()
        
        # Test JSON extraction
        json_file = Path("Exam_Raw_Data_JSON/sample_exam.json")
        if json_file.exists():
            print(f"Testing JSON extraction: {json_file.name}")
            data = converter.extract_data_from_json(str(json_file))
            if data:
                print(f"  ✅ Extracted {len(data.get('questions', []))} questions")
                print(f"  ✅ Time limit: {data.get('timeLimitInMinutes', 'Not specified')} minutes")
            else:
                print("  ❌ Failed to extract JSON data")
        else:
            print("  ⚠️ JSON sample file not found")
        
        # Test HTML extraction
        html_file = Path("Exam_HTML_Raw_Data/sample_exam.html")
        if html_file.exists():
            print(f"\nTesting HTML extraction: {html_file.name}")
            data = converter.extract_data_from_html(str(html_file))
            if data:
                print(f"  ✅ Extracted {len(data.get('questions', []))} questions")
                print(f"  ✅ Time limit: {data.get('timeLimitInMinutes', 'Not specified')} minutes")
            else:
                print("  ❌ Failed to extract HTML data")
        else:
            print("  ⚠️ HTML sample file not found")
        
        print("✅ Data extraction test completed")
        
    except Exception as e:
        print(f"❌ Data extraction test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main test runner"""
    print("🧪 Robust Exam Converter Test Suite")
    print("=" * 60)
    print("This script tests the documented converter functionality")
    print("=" * 60)
    
    # Run tests
    test_multi_answer_detection()
    test_format_detection()
    create_sample_exam_files()
    test_data_extraction()
    
    print("\n" + "=" * 60)
    print("🎯 TEST SUITE SUMMARY")
    print("=" * 60)
    print("All basic functionality tests completed!")
    print("\nNext steps:")
    print("1. Start your Flask app: python start_pcep_app.py")
    print("2. Test database import: python robust_exam_converter_documented.py")
    print("3. Check results at: http://localhost:5000/api/questions")
    
    print("\n💡 Tips:")
    print("- Check the log files for detailed processing information")
    print("- Use the multi-answer detection for custom question analysis")
    print("- Modify sample files to test edge cases")
    print("=" * 60)

if __name__ == "__main__":
    main()

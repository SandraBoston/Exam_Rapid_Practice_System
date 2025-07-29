#!/usr/bin/env python3
"""
Test script for Enhanced Converter Phase 1 Features
Tests format detection and multi-answer detection improvements
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

from robust_exam_converter import RobustExamConverter

def test_format_detection():
    """Test enhanced format detection capabilities"""
    print("🔍 Testing Enhanced Format Detection")
    print("=" * 50)
    
    converter = RobustExamConverter()
    
    # Test cases for format detection
    test_cases = [
        ("test.json", "json"),
        ("test.html", "html"),
        ("test.htm", "html"),
        ("PE1 -- Module 2 Test_20250610_v1.html", "html"),
        ("PCEP_Exam_Module_3_raw_data.json", "json"),
    ]
    
    for filename, expected in test_cases:
        # Create temporary test file
        test_file = Path(filename)
        
        # Create appropriate content based on expected format
        if expected == "json":
            content = '{"questions": [{"id": 1, "question": "Test?"}]}'
        else:
            content = '<html><script>let data = {"questions": []};</script></html>'
        
        try:
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            detected = converter.detect_file_format(str(test_file))
            status = "✅" if detected == expected else "❌"
            print(f"{status} {filename} -> Expected: {expected}, Got: {detected}")
            
        except Exception as e:
            print(f"❌ {filename} -> Error: {e}")
        finally:
            # Clean up test file
            if test_file.exists():
                test_file.unlink()
    
    print()

def test_multi_answer_detection():
    """Test enhanced multi-answer detection"""
    print("🎯 Testing Enhanced Multi-Answer Detection")
    print("=" * 50)
    
    converter = RobustExamConverter()
    
    # Test cases with various multi-answer patterns
    test_cases = [
        # (question_text, options, expected_type, expected_count)
        ("Select two correct answers:", None, "multi-select", 2),
        ("Choose three answers from the following:", None, "multi-select", 3),
        ("Mark all that apply:", None, "multi-select", 99),
        ("(Select two)", None, "multi-select", 2),
        ("Which statements are correct?", None, "multi-select", 2),
        ("What is the output of this code?", None, "single-select", 1),
        ("Identify the correct answer:", None, "single-select", 1),
        ("Select one answer:", None, "single-select", 1),
        
        # Test with checkbox indicators in options
        ("Which is correct?", ["[] Option A", "[] Option B"], "multi-select", 2),
        ("What happens?", ["() Option A", "() Option B"], "single-select", 1),
    ]
    
    for question_text, options, expected_type, expected_count in test_cases:
        try:
            result = converter.detect_multi_answer_requirement(question_text, options)
            
            detected_type = result.get("type")
            detected_count = result.get("required_answers", 1)
            confidence = result.get("confidence", 0)
            
            type_match = detected_type == expected_type
            count_match = detected_count == expected_count or (expected_count == 99 and detected_count > 1)
            
            status = "✅" if type_match and count_match else "❌"
            
            print(f"{status} \"{question_text[:40]}...\"")
            print(f"    Expected: {expected_type}, {expected_count} answers")
            print(f"    Detected: {detected_type}, {detected_count} answers (confidence: {confidence:.2f})")
            print()
            
        except Exception as e:
            print(f"❌ Error testing \"{question_text[:30]}...\": {e}")
            print()

def test_data_validation():
    """Test data validation functionality"""
    print("✅ Testing Data Validation")
    print("=" * 50)
    
    converter = RobustExamConverter()
    
    # Test cases for validation
    test_cases = [
        # Valid data
        {
            "data": {
                "questions": [
                    {
                        "id": 1,
                        "question": "What is Python?",
                        "options": ["A language", "A snake", "A tool"]
                    }
                ]
            },
            "expected_valid": True,
            "description": "Valid exam data"
        },
        
        # Missing questions
        {
            "data": {},
            "expected_valid": False,
            "description": "Missing questions field"
        },
        
        # Empty questions
        {
            "data": {"questions": []},
            "expected_valid": False,
            "description": "Empty questions list"
        },
        
        # Invalid question structure
        {
            "data": {
                "questions": [
                    {
                        "id": 1,
                        # Missing question text
                        "options": ["A", "B"]
                    }
                ]
            },
            "expected_valid": True,  # Should pass with warnings
            "description": "Question missing text"
        }
    ]
    
    for test_case in test_cases:
        try:
            is_valid, errors = converter.validate_exam_data(test_case["data"], "test_file.json")
            expected = test_case["expected_valid"]
            
            status = "✅" if is_valid == expected else "❌"
            print(f"{status} {test_case['description']}")
            print(f"    Expected valid: {expected}, Got: {is_valid}")
            if errors:
                print(f"    Errors: {len(errors)} found")
                for error in errors[:2]:  # Show first 2 errors
                    print(f"      - {error}")
            print()
            
        except Exception as e:
            print(f"❌ Error testing {test_case['description']}: {e}")
            print()

def main():
    """Run all tests"""
    print("🚀 Testing Enhanced Converter Phase 1 Features")
    print("=" * 70)
    print()
    
    test_format_detection()
    test_multi_answer_detection()
    test_data_validation()
    
    print("🏁 Phase 1 Testing Complete!")
    print("=" * 70)

if __name__ == "__main__":
    main()

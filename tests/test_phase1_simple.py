#!/usr/bin/env python3
"""
Simple test for Phase 1 enhancements - no database dependency
Tests just the format detection and multi-answer detection
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

# Import just the converter class without database dependencies
from robust_exam_converter import RobustExamConverter

def test_format_detection_simple():
    """Test enhanced format detection"""
    print("🔍 Testing Enhanced Format Detection")
    print("=" * 50)
    
    converter = RobustExamConverter()
    
    # Test extension-based detection
    test_cases = [
        ("test.json", "json"),
        ("test.html", "html"),
        ("PE1_Module_2_Test.html", "html"),
        ("PCEP_raw_data.json", "json"),
    ]
    
    for filename, expected in test_cases:
        # Create temporary test file
        test_file = Path(filename)
        
        # Create appropriate content
        if expected == "json":
            content = '{"questions": [{"id": 1, "question": "Test?"}]}'
        else:
            content = '<html><head></head><body><script>let data = {"questions": []};</script></body></html>'
        
        try:
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            detected = converter.detect_file_format(str(test_file))
            status = "✅" if detected == expected else "❌"
            print(f"{status} {filename} -> Expected: {expected}, Got: {detected}")
            
        except Exception as e:
            print(f"❌ {filename} -> Error: {e}")
        finally:
            if test_file.exists():
                test_file.unlink()
    
    print()

def test_multi_answer_detection_simple():
    """Test enhanced multi-answer detection"""
    print("🎯 Testing Enhanced Multi-Answer Detection")
    print("=" * 50)
    
    converter = RobustExamConverter()
    
    # Test cases
    test_cases = [
        ("Select two correct answers:", "multi-select", 2),
        ("Choose three answers:", "multi-select", 3),
        ("Mark all that apply:", "multi-select", 99),
        ("(Select two)", "multi-select", 2),
        ("Which statements are correct?", "multi-select", 2),
        ("What is the output?", "single-select", 1),
        ("Select one answer:", "single-select", 1),
    ]
    
    for question_text, expected_type, expected_count in test_cases:
        try:
            result = converter.detect_multi_answer_requirement(question_text)
            
            detected_type = result.get("type", "unknown")
            detected_count = result.get("required_answers", 0)
            confidence = result.get("confidence", 0)
            
            type_match = detected_type == expected_type
            count_match = detected_count == expected_count or (expected_count == 99 and detected_count > 1)
            
            status = "✅" if type_match and count_match else "❌"
            
            print(f"{status} \"{question_text}\"")
            print(f"    Expected: {expected_type}, {expected_count}")
            print(f"    Detected: {detected_type}, {detected_count} (conf: {confidence:.2f})")
            print()
            
        except Exception as e:
            print(f"❌ Error with \"{question_text}\": {e}")
            print()

def main():
    """Run simple tests"""
    print("🚀 Testing Phase 1 Enhancements (Simple Mode)")
    print("=" * 60)
    print()
    
    test_format_detection_simple()
    test_multi_answer_detection_simple()
    
    print("✅ Phase 1 Simple Testing Complete!")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Process Real PCEP Exam Files
=============================
This script processes all the real exam files in the Exam_HTML_Raw_Data directory
using the robust converter we just tested.
"""

import sys
import os
from pathlib import Path

# Add converter to path
sys.path.insert(0, 'src/converters_2_Evaluate')

def main():
    try:
        from robust_exam_converter_documented import RobustExamConverter
        
        print("🚀 PROCESSING REAL PCEP EXAM FILES")
        print("=" * 60)
        
        # Check directory exists
        exam_dir = Path("Exam_HTML_Raw_Data")
        if not exam_dir.exists():
            print(f"❌ Directory not found: {exam_dir}")
            return
        
        # List all HTML files
        html_files = list(exam_dir.glob("*.html"))
        json_files = list(exam_dir.glob("*.json"))
        
        print(f"📁 Found in {exam_dir}:")
        print(f"   📄 HTML files: {len(html_files)}")
        print(f"   📄 JSON files: {len(json_files)}")
        
        if not html_files and not json_files:
            print("⚠️  No HTML or JSON files found to process")
            return
        
        # Initialize converter
        converter = RobustExamConverter()
        
        print(f"\n🔄 Processing files...")
        print("=" * 60)
        
        # Process HTML files
        for i, html_file in enumerate(html_files, 1):
            print(f"\n📄 Processing HTML file {i}/{len(html_files)}: {html_file.name}")
            try:
                # Test format detection
                format_type = converter.detect_file_format(str(html_file))
                print(f"   🔍 Format detected: {format_type}")
                
                # Test data extraction
                if format_type == 'html':
                    data = converter.extract_data_from_html(str(html_file))
                else:
                    data = converter.extract_data_from_json(str(html_file))
                
                if data:
                    questions = data.get('questions', [])
                    print(f"   📊 Questions extracted: {len(questions)}")
                    print(f"   ⏰ Time limit: {data.get('timeLimitInMinutes', 'Not specified')} minutes")
                    
                    # Analyze first few questions for multi-answer detection
                    if questions:
                        print(f"   🧠 Question analysis:")
                        for j, q in enumerate(questions[:3]):  # First 3 questions
                            question_text = q.get('question', '')
                            options = q.get('options', [])
                            result = converter.detect_multi_answer_requirement(question_text, options)
                            print(f"      Q{j+1}: {result['type']} ({result['required_answers']} answers, {result['confidence']:.2f} confidence)")
                        
                        if len(questions) > 3:
                            print(f"      ... and {len(questions) - 3} more questions")
                    
                    # Validate data
                    is_valid, errors = converter.validate_exam_data(data, str(html_file))
                    print(f"   ✅ Validation: {'PASSED' if is_valid else 'FAILED'}")
                    if errors:
                        print(f"   ⚠️  Validation issues: {len(errors)}")
                        for error in errors[:2]:  # Show first 2 errors
                            print(f"      - {error}")
                    
                    print(f"   ✅ File processed successfully")
                else:
                    print(f"   ❌ Failed to extract data from {html_file.name}")
                    
            except Exception as e:
                print(f"   ❌ Error processing {html_file.name}: {e}")
        
        # Process JSON files
        for i, json_file in enumerate(json_files, 1):
            print(f"\n📄 Processing JSON file {i}/{len(json_files)}: {json_file.name}")
            try:
                # Test format detection
                format_type = converter.detect_file_format(str(json_file))
                print(f"   🔍 Format detected: {format_type}")
                
                # Test data extraction
                data = converter.extract_data_from_json(str(json_file))
                
                if data:
                    questions = data.get('questions', [])
                    print(f"   📊 Questions extracted: {len(questions)}")
                    print(f"   ⏰ Time limit: {data.get('timeLimitInMinutes', 'Not specified')} minutes")
                    
                    # Analyze first few questions
                    if questions:
                        print(f"   🧠 Question analysis:")
                        for j, q in enumerate(questions[:3]):
                            question_text = q.get('question', '')
                            options = q.get('options', [])
                            result = converter.detect_multi_answer_requirement(question_text, options)
                            print(f"      Q{j+1}: {result['type']} ({result['required_answers']} answers, {result['confidence']:.2f} confidence)")
                        
                        if len(questions) > 3:
                            print(f"      ... and {len(questions) - 3} more questions")
                    
                    # Validate data
                    is_valid, errors = converter.validate_exam_data(data, str(json_file))
                    print(f"   ✅ Validation: {'PASSED' if is_valid else 'FAILED'}")
                    if errors:
                        print(f"   ⚠️  Validation issues: {len(errors)}")
                    
                    print(f"   ✅ File processed successfully")
                else:
                    print(f"   ❌ Failed to extract data from {json_file.name}")
                    
            except Exception as e:
                print(f"   ❌ Error processing {json_file.name}: {e}")
        
        # Summary
        print(f"\n" + "=" * 60)
        print("📊 PROCESSING SUMMARY")
        print("=" * 60)
        print(f"🗂️  Total files found: {len(html_files) + len(json_files)}")
        print(f"📄 HTML files: {len(html_files)}")
        print(f"📄 JSON files: {len(json_files)}")
        print("\n✅ Real exam file processing completed!")
        print("\n💡 Next steps:")
        print("   1. If files processed successfully, they contain valid exam data")
        print("   2. You can now import them to database using the full converter")
        print("   3. Check the question analysis results above")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure the robust_exam_converter_documented.py is in the correct location")
    except Exception as e:
        print(f"❌ Processing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

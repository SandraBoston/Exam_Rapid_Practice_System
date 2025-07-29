#!/usr/bin/env python3
"""
Lean HTML Exam Data Extractor
=============================

Purpose: Extract exam questions from HTML files and serialize to portable data format
         for the PCEP ETL pipeline.

ETL Pipeline - EXTRACT Phase:
- Extract JSON data from HTML exam files
- Convert to clean data structures
- Include exam metadata (title, exam_ID, etc.)
- Preserve HTML formatting for reliable database storage
- Output human-readable serialized data files

Usage:
    python lean_exam_converter.py input.html output.data [exam_title]

Output: Serialized data file with exam metadata and questions (portable format)

Author: PCEP Rapid Practice App
Date: 2025-06-27
Version: 4.0 (ETL Extract Phase)
"""

import json
import re
import sys
import os
from pathlib import Path
from datetime import datetime


class LeanExamExtractor:
    """Extract exam data from HTML and serialize to portable data format."""
    
    def __init__(self):
        self.exam_metadata = {}
        
    def extract_json_from_html(self, html_file_path):
        """Extract the JSON data embedded in the HTML file."""
        try:
            with open(html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Extract the JavaScript data object
            # Pattern to find: let data = { ... };
            pattern = r'let\s+data\s*=\s*({.*?});'
            match = re.search(pattern, html_content, re.DOTALL)
            
            if not match:
                print(f"❌ No JavaScript data object found in {html_file_path}")
                return None
                
            json_str = match.group(1)
            
            # Parse JSON
            exam_data = json.loads(json_str)
            print(f"✅ Extracted {len(exam_data.get('questions', []))} questions from HTML")
            
            return exam_data
            
        except FileNotFoundError:
            print(f"❌ File not found: {html_file_path}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            return None
        except Exception as e:
            print(f"❌ Error reading HTML file: {e}")
            return None
    
    def extract_exam_metadata(self, html_file_path, exam_title=None):
        """Extract or generate exam metadata."""
        file_name = Path(html_file_path).stem
        
        # Try to extract title from filename or use provided title
        if exam_title:
            title = exam_title
        elif "Module" in file_name:
            # Extract module info from filename like "PE1 -- Module 4 Test_20250610_v1"
            match = re.search(r'Module\s+(\d+)', file_name, re.IGNORECASE)
            if match:
                module_num = match.group(1)
                title = f"PCEP Module {module_num} Test"
            else:
                title = file_name.replace('_', ' ')
        else:
            title = file_name.replace('_', ' ')
        
        # Generate exam ID from filename
        exam_id = re.sub(r'[^\w]', '_', file_name).lower()
        
        self.exam_metadata = {
            'title': title,
            'exam_id': exam_id,
            'source_file': file_name,
            'extraction_date': datetime.now().strftime('%Y-%m-%d'),
            'converter_version': '3.0'
        }
        
        return self.exam_metadata
    
    def convert_questions_for_database(self, exam_data):
        """Convert exam questions to database-ready format."""
        if not exam_data or 'questions' not in exam_data:
            print("❌ No questions found in exam data")
            return []
        
        converted_questions = []
        
        for i, question in enumerate(exam_data['questions'], 1):
            # Keep the structure simple and database-friendly
            db_question = {
                'question_id': question.get('id', i),
                'question_text': question.get('question', ''),  # Keep HTML tags
                'question_type': question.get('type', 'Single Choice'),
                'options': [],
                'metadata': {
                    'order': i,
                    'original_type': question.get('type')
                }
            }
            
            # Process options (keep HTML formatting)
            for j, option in enumerate(question.get('options', [])):
                db_option = {
                    'option_id': option.get('id', j),
                    'option_text': option.get('option', ''),  # Keep HTML tags
                    'option_order': j
                }
                db_question['options'].append(db_option)
            
            converted_questions.append(db_question)
            
        print(f"✅ Converted {len(converted_questions)} questions for database")
        return converted_questions
    
    def serialize_exam_data(self, questions, metadata, output_file):
        """Serialize exam data to portable text format."""
        
        # Create the serialized data content
        content = f'''# PCEP Exam Data File
# Auto-generated serialized exam data for ETL pipeline
# Format: Human-readable Python data structures
# Generated: {metadata['extraction_date']}

# EXAM_METADATA
{json.dumps(metadata, indent=2)}

# EXAM_QUESTIONS  
{json.dumps(questions, indent=2, ensure_ascii=False)}

# END_OF_DATA
'''
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Serialized data: {output_file}")
        return True


def print_usage():
    """Print usage instructions."""
    print("Lean HTML Exam Data Extractor (ETL Extract Phase)")
    print("=" * 50)
    print("Usage:")
    print("    python lean_exam_converter.py input.html output.data [exam_title]")
    print("")
    print("Examples:")
    print("    python lean_exam_converter.py module4.html module4_exam.data")
    print("    python lean_exam_converter.py exam.html exam.data \"PCEP Module 3 Test\"")
    print("")
    print("Arguments:")
    print("    input.html   : HTML file containing exam data")
    print("    output.data  : Serialized data file to generate")
    print("    exam_title   : Optional exam title (auto-detected if not provided)")


def main():
    """Main extraction function for ETL pipeline."""
    if len(sys.argv) < 3:
        print_usage()
        return
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    exam_title = sys.argv[3] if len(sys.argv) > 3 else None
    
    print("ETL Extract Phase - Starting Data Extraction...")
    print(f"📁 Input: {input_file}")
    print(f"📁 Output: {output_file}")
    print("-" * 50)
    
    # Create extractor
    extractor = LeanExamExtractor()
    
    # Extract metadata
    metadata = extractor.extract_exam_metadata(input_file, exam_title)
    print(f"📋 Exam Title: {metadata['title']}")
    print(f"🔑 Exam ID: {metadata['exam_id']}")
    
    # Extract JSON from HTML
    exam_data = extractor.extract_json_from_html(input_file)
    if not exam_data:
        print("❌ Failed to extract exam data")
        return
    
    # Convert for database
    questions = extractor.convert_questions_for_database(exam_data)
    if not questions:
        print("❌ No questions to convert")
        return
    
    # Serialize to data file
    success = extractor.serialize_exam_data(questions, metadata, output_file)
    
    if success:
        print("-" * 50)
        print("✅ Extract phase completed successfully!")
        print(f"📊 Total Questions: {len(questions)}")
        print(f"📁 Data File: {output_file}")
        print("🔄 Ready for Transform/Load phases!")
    else:
        print("❌ Extract phase failed")


if __name__ == "__main__":
    main()

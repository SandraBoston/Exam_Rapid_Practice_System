#!/usr/bin/env python3
"""
ENHANCED METADATA-AWARE Converter for PCEP Exam Data
===================================================

OVERVIEW:
---------
Enhanced version of the robust converter with advanced metadata extraction,
file type recognition, and comprehensive source tracking capabilities.

NEW FEATURES:
-------------
1. **Intelligent File Type Recognition**: Detects quiz/test/exam patterns in filenames
2. **Comprehensive Metadata Extraction**: Extracts ID, name, time limits, and source info
3. **Source Filename Tracking**: Maintains full audit trail of file origins
4. **Enhanced Database Schema Support**: Works with extended Exam model fields
5. **Flexible Naming Logic**: Derives meaningful exam names from multiple sources

ENHANCED CAPABILITIES:
----------------------
- File type classification (quiz/test/exam/assessment)
- JSON metadata extraction (id, timeLimitInMinutes, etc.)
- Source filename preservation in database
- Enhanced exam naming from filename + JSON data
- Improved duplicate detection using external IDs
- Comprehensive import reporting with metadata summary

USAGE:
------
```python
from enhanced_metadata_converter import EnhancedMetadataConverter

converter = EnhancedMetadataConverter()

# Process single file with metadata extraction
result = converter.process_file_with_metadata('path/to/exam.json')

# Batch process with full metadata reporting
results = converter.batch_process_with_metadata('path/to/json_folder/')

# Get comprehensive import summary
summary = converter.get_import_summary()
```

AUTHOR: PCEP Exam Accelerator System
DATE: 2025-01-15
VERSION: 2.0 (Enhanced Metadata Edition)
"""

import os
import re
import json
import logging
import traceback
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime

# Database imports
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Model imports - Use dependency injection to avoid circular imports
try:
    # These will be injected by the calling code to avoid circular imports
    Exam = None
    Question = None
    Answer = None
    Topic = None
    db = None
    print("⚠️ Models will be injected by calling code to avoid circular imports")
except Exception as e:
    print(f"Warning: Model setup issue: {e}")
    Exam = None
    Question = None
    Answer = None
    Topic = None
    db = None
    Topic = None

class EnhancedMetadataConverter:
    """
    Enhanced converter with intelligent metadata extraction and file type recognition.
    """
    
    def __init__(self, session=None, models=None):
        """
        Initialize the enhanced converter.
        
        Args:
            session: SQLAlchemy session object (optional)
            models: Dictionary containing model classes {'Exam': ExamClass, 'Question': QuestionClass, etc.}
        """
        self.session = session
        self.processed_files = []
        self.errors = []
        self.import_summary = {
            'total_files': 0,
            'successful_imports': 0,
            'failed_imports': 0,
            'file_types': {'quiz': 0, 'test': 0, 'exam': 0, 'assessment': 0},
            'total_questions': 0,
            'total_exams': 0,
            'processing_time': 0
        }
        
        # Inject models if provided
        if models:
            global Exam, Question, Answer, Topic
            Exam = models.get('Exam')
            Question = models.get('Question') 
            Answer = models.get('Answer')
            Topic = models.get('Topic')
            print("✅ Models injected successfully")
            
        self.import_summary['processing_time'] = 0
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, 
                          format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
    def detect_file_type(self, filename: str) -> str:
        """
        Intelligently detect file type based on filename patterns.
        
        Args:
            filename (str): Name of the file to analyze
            
        Returns:
            str: Detected file type ('quiz', 'test', 'exam', 'assessment')
        """
        filename_lower = filename.lower()
        
        # Primary pattern matching
        if 'quiz' in filename_lower:
            return 'quiz'
        elif 'test' in filename_lower:
            return 'test'
        elif 'exam' in filename_lower:
            return 'exam'
        else:
            return 'assessment'  # fallback for any assessment material
    
    def extract_exam_metadata(self, json_data: Dict, source_filename: str) -> Dict[str, Any]:
        """
        Extract comprehensive metadata from JSON data and filename.
        
        Args:
            json_data (dict): Parsed JSON data from file
            source_filename (str): Original filename
            
        Returns:
            dict: Comprehensive metadata dictionary
        """
        metadata = {
            'exam_external_id': json_data.get('id'),
            'source_filename': source_filename,
            'file_type': self.detect_file_type(source_filename),
            'time_limit_minutes': json_data.get('timeLimitInMinutes'),
            'show_review': json_data.get('showReview', False),
            'question_count': len(json_data.get('questions', [])),
            'extracted_at': datetime.now().isoformat(),
            'original_json_keys': list(json_data.keys())
        }
        
        # Add any additional top-level metadata
        for key, value in json_data.items():
            if key not in ['questions'] and isinstance(value, (str, int, float, bool)):
                metadata[f'original_{key}'] = value
                
        return metadata
    
    def derive_exam_name(self, filename: str, json_data: Dict) -> str:
        """
        Derive a meaningful exam name from filename and JSON data.
        
        Args:
            filename (str): Source filename
            json_data (dict): Parsed JSON data
            
        Returns:
            str: Derived exam name
        """
        # Remove file extension and clean filename
        base_name = Path(filename).stem
        
        # Replace underscores and clean up
        cleaned_name = base_name.replace('_', ' ').replace('-', ' ')
        
        # Check for title in JSON data
        if 'title' in json_data and json_data['title']:
            return json_data['title']
        
        # Check for name field
        if 'name' in json_data and json_data['name']:
            return json_data['name']
        
        # Use filename with some intelligent formatting
        # Capitalize first letter of each word
        formatted_name = ' '.join(word.capitalize() for word in cleaned_name.split())
        
        return formatted_name
    
    def extract_json_from_content(self, content: str) -> Optional[Dict]:
        """
        Extract JSON data from file content (supports both JSON and HTML with embedded JS).
        
        Args:
            content (str): File content
            
        Returns:
            dict: Extracted JSON data or None if extraction fails
        """
        # Try direct JSON parsing first
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        
        # Try extracting from HTML/JavaScript patterns
        patterns = [
            r'let\s+data\s*=\s*({.*?});',
            r'var\s+data\s*=\s*({.*?});',
            r'const\s+data\s*=\s*({.*?});',
            r'data\s*=\s*({.*?});'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            if matches:
                try:
                    return json.loads(matches[0])
                except json.JSONDecodeError:
                    continue
        
        return None
    
    def validate_json_structure(self, data: Dict) -> Tuple[bool, str]:
        """
        Validate that JSON data has required structure for exam processing.
        
        Args:
            data (dict): JSON data to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not isinstance(data, dict):
            return False, "Data is not a dictionary"
        
        if 'questions' not in data:
            return False, "Missing 'questions' key"
        
        if not isinstance(data['questions'], list):
            return False, "'questions' must be a list"
        
        if len(data['questions']) == 0:
            return False, "No questions found in data"
        
        # Validate first question structure
        first_question = data['questions'][0]
        if not isinstance(first_question, dict):
            return False, "Questions must be dictionaries"
        
        # Check for required fields - support both 'answers' and 'options'
        if 'question' not in first_question:
            return False, "Question missing required field: question"
        
        if 'answers' not in first_question and 'options' not in first_question:
            return False, "Question missing required field: answers or options"
        
        return True, "Valid structure"
    
    def process_file_with_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Process a single file with comprehensive metadata extraction.
        
        Args:
            file_path (str): Path to the file to process
            
        Returns:
            dict: Processing result with metadata
        """
        start_time = datetime.now()
        result = {
            'file_path': file_path,
            'filename': os.path.basename(file_path),
            'success': False,
            'metadata': {},
            'exam_id': None,
            'questions_imported': 0,
            'errors': [],
            'processing_time': 0
        }
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract JSON data
            json_data = self.extract_json_from_content(content)
            if not json_data:
                result['errors'].append("Failed to extract JSON data from file")
                return result
            
            # Validate structure
            is_valid, error_msg = self.validate_json_structure(json_data)
            if not is_valid:
                result['errors'].append(f"Invalid JSON structure: {error_msg}")
                return result
            
            # Extract metadata
            metadata = self.extract_exam_metadata(json_data, result['filename'])
            result['metadata'] = metadata
            
            # Import to database if session available
            if self.session:
                exam_id = self._import_to_database(json_data, metadata)
                result['exam_id'] = exam_id
                result['questions_imported'] = len(json_data['questions'])
            
            result['success'] = True
            self.logger.info(f"Successfully processed {result['filename']} - "
                           f"Type: {metadata['file_type']}, "
                           f"Questions: {metadata['question_count']}")
            
        except Exception as e:
            error_msg = f"Error processing {file_path}: {str(e)}"
            result['errors'].append(error_msg)
            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())
        
        finally:
            result['processing_time'] = (datetime.now() - start_time).total_seconds()
        
        return result
    
    def _import_to_database(self, json_data: Dict, metadata: Dict) -> Optional[int]:
        """
        Import exam data to database with metadata.
        
        Args:
            json_data (dict): JSON exam data
            metadata (dict): Extracted metadata
            
        Returns:
            int: Exam ID if successful, None otherwise
        """
        try:
            # Check for existing exam by external ID
            existing_exam = None
            if metadata['exam_external_id']:
                existing_exam = self.session.query(Exam).filter(
                    Exam.exam_metadata.contains(f'"exam_external_id": {metadata["exam_external_id"]}')
                ).first()
            
            if existing_exam:
                self.logger.info(f"Exam with external ID {metadata['exam_external_id']} already exists")
                return existing_exam.id
            
            # Create new exam
            exam_name = self.derive_exam_name(metadata['source_filename'], json_data)
            
            exam = Exam(
                title=exam_name,
                description=f"Imported from {metadata['source_filename']} - {metadata['file_type'].title()}",
                time_limit=metadata.get('time_limit_minutes', 60) * 60,  # Convert to seconds
                total_questions=metadata['question_count'],
                source_file=metadata['source_filename'],
                version='1.0',
                is_active=True
            )
            
            # Set metadata
            exam.set_metadata(metadata)
            
            self.session.add(exam)
            self.session.flush()  # Get the exam ID
            
            # Import questions
            for idx, question_data in enumerate(json_data['questions']):
                self._import_question(question_data, exam.id, idx + 1)
            
            self.session.commit()
            
            self.logger.info(f"Successfully imported exam: {exam_name} (ID: {exam.id})")
            return exam.id
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Database import error: {str(e)}")
            raise
    
    def _import_question(self, question_data: Dict, exam_id: int, order: int):
        """
        Import a single question with answers/options.
        
        Args:
            question_data (dict): Question data from JSON
            exam_id (int): Parent exam ID
            order (int): Question order in exam
        """
        # Create question
        question = Question(
            original_id=question_data.get('id', str(order)),
            text=question_data['question'],
            difficulty=question_data.get('difficulty', 1),
            exam_id=exam_id,
            question_order=order,
            explanation=question_data.get('explanation', '')
        )
        
        self.session.add(question)
        self.session.flush()  # Get question ID
        
        # Import answers - support both 'answers' and 'options' fields
        answer_data = question_data.get('answers', question_data.get('options', []))
        
        for answer_item in answer_data:
            # Handle different answer data structures
            if isinstance(answer_item, dict):
                answer_text = answer_item.get('text', answer_item.get('option', ''))
                is_correct = answer_item.get('correct', answer_item.get('isCorrect', False))
                explanation = answer_item.get('explanation', '')
            else:
                # Handle simple string answers
                answer_text = str(answer_item)
                is_correct = False
                explanation = ''
            
            answer = Answer(
                text=answer_text,
                is_correct=is_correct,
                question_id=question.id,
                explanation=explanation
            )
            self.session.add(answer)
    
    def batch_process_with_metadata(self, folder_path: str, file_pattern: str = "*.json") -> List[Dict]:
        """
        Process multiple files in a folder with metadata extraction.
        
        Args:
            folder_path (str): Path to folder containing files
            file_pattern (str): Glob pattern for files to process
            
        Returns:
            list: List of processing results
        """
        start_time = datetime.now()
        results = []
        
        # Find all matching files
        folder = Path(folder_path)
        files = list(folder.glob(file_pattern))
        
        self.import_summary['total_files'] = len(files)
        
        self.logger.info(f"Starting batch processing of {len(files)} files...")
        
        for file_path in files:
            result = self.process_file_with_metadata(str(file_path))
            results.append(result)
            
            # Update summary
            if result['success']:
                self.import_summary['successful_imports'] += 1
                self.import_summary['total_questions'] += result['questions_imported']
                file_type = result['metadata'].get('file_type', 'assessment')
                self.import_summary['file_types'][file_type] += 1
                if result['exam_id']:
                    self.import_summary['total_exams'] += 1
            else:
                self.import_summary['failed_imports'] += 1
        
        self.import_summary['processing_time'] = (datetime.now() - start_time).total_seconds()
        
        self.logger.info(f"Batch processing complete. "
                        f"Success: {self.import_summary['successful_imports']}, "
                        f"Failed: {self.import_summary['failed_imports']}")
        
        return results
    
    def get_import_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive import summary with metadata breakdown.
        
        Returns:
            dict: Import summary with statistics
        """
        return self.import_summary.copy()
    
    def generate_metadata_report(self, results: List[Dict]) -> str:
        """
        Generate a detailed metadata report from processing results.
        
        Args:
            results (list): List of processing results
            
        Returns:
            str: Formatted metadata report
        """
        report = []
        report.append("=" * 80)
        report.append("ENHANCED METADATA EXTRACTION REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary section
        summary = self.get_import_summary()
        report.append("SUMMARY:")
        report.append("-" * 40)
        report.append(f"Total Files Processed: {summary['total_files']}")
        report.append(f"Successful Imports: {summary['successful_imports']}")
        report.append(f"Failed Imports: {summary['failed_imports']}")
        report.append(f"Total Exams Created: {summary['total_exams']}")
        report.append(f"Total Questions Imported: {summary['total_questions']}")
        report.append(f"Processing Time: {summary['processing_time']:.2f} seconds")
        report.append("")
        
        # File type breakdown
        report.append("FILE TYPE DISTRIBUTION:")
        report.append("-" * 40)
        for file_type, count in summary['file_types'].items():
            if count > 0:
                report.append(f"{file_type.title()}: {count}")
        report.append("")
        
        # Detailed file results
        report.append("DETAILED RESULTS:")
        report.append("-" * 40)
        for result in results:
            status = "✓ SUCCESS" if result['success'] else "✗ FAILED"
            report.append(f"{status}: {result['filename']}")
            
            if result['success'] and result['metadata']:
                metadata = result['metadata']
                report.append(f"  - Type: {metadata.get('file_type', 'unknown').title()}")
                report.append(f"  - External ID: {metadata.get('exam_external_id', 'N/A')}")
                report.append(f"  - Questions: {metadata.get('question_count', 0)}")
                if metadata.get('time_limit_minutes'):
                    report.append(f"  - Time Limit: {metadata['time_limit_minutes']} minutes")
                if result['exam_id']:
                    report.append(f"  - Database ID: {result['exam_id']}")
            
            if result['errors']:
                for error in result['errors']:
                    report.append(f"  - ERROR: {error}")
            
            report.append("")
        
        return "\n".join(report)


def main():
    """
    Example usage of the Enhanced Metadata Converter.
    """
    print("Enhanced Metadata Converter - Example Usage")
    print("=" * 50)
    
    # Initialize converter
    converter = EnhancedMetadataConverter()
    
    # Example: Process files in the extracted JSON folder
    json_folder = r"C:\Users\Lucas\OneDrive\Desktop\00_PythonWIP\PCEP_Rapid_Practice_System\Exam_HTML_Raw_Data_JSON_ONLY"
    
    if os.path.exists(json_folder):
        print(f"Processing files in: {json_folder}")
        results = converter.batch_process_with_metadata(json_folder)
        
        # Generate and display report
        report = converter.generate_metadata_report(results)
        print(report)
        
        # Save report to file
        report_path = "enhanced_metadata_extraction_report.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\nReport saved to: {report_path}")
    else:
        print(f"Folder not found: {json_folder}")
        print("Please verify the path and try again.")


if __name__ == "__main__":
    main()

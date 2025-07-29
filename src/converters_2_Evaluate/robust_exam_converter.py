#!/usr/bin/env python3
"""
ROBUST Multi-Dataset Converter for PCEP Exam Data
Handles HTML, JSON, batch processing, and robust error handling

Lessons Learned Integration:
1. Automatic multi-answer detection
2. Proper metadata handling  
3. Duplicate prevention
4. Batch processing
5. Comprehensive error handling
"""

import sys
import json
import re
import os
from datetime import datetime
import logging
from pathlib import Path

sys.path.insert(0, 'src')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'converter_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RobustExamConverter:
    """Enhanced converter for processing multiple exam datasets"""
    
    def __init__(self):
        self.stats = {
            'files_processed': 0,
            'exams_created': 0,
            'questions_imported': 0,
            'answers_imported': 0,
            'errors': 0,
            'skipped_duplicates': 0
        }
        
        # Enhanced multi-answer detection patterns with confidence scoring
        self.multi_answer_patterns = [
            # Explicit multi-answer instructions
            (r'select\s+(\w+)\s+(?:of\s+the\s+)?(?:correct\s+)?answers?', 0.95),
            (r'choose\s+(\w+)\s+(?:of\s+the\s+)?(?:correct\s+)?answers?', 0.95),
            (r'pick\s+(\w+)\s+(?:of\s+the\s+)?(?:correct\s+)?answers?', 0.90),
            (r'mark\s+(\w+)\s+(?:of\s+the\s+)?(?:correct\s+)?answers?', 0.90),
            (r'identify\s+(\w+)\s+(?:correct\s+)?answers?', 0.85),
            
            # Parenthetical instructions
            (r'\(\s*select\s+(\w+)\s*\)', 0.98),
            (r'\(\s*choose\s+(\w+)\s*\)', 0.98),
            (r'\(\s*mark\s+(\w+)\s*\)', 0.95),
            
            # "All that apply" patterns
            (r'mark\s+all\s+that\s+apply', 0.99),
            (r'select\s+all\s+that\s+apply', 0.99),
            (r'choose\s+all\s+that\s+apply', 0.99),
            (r'identify\s+all\s+that\s+apply', 0.95),
            
            # Multiple options patterns
            (r'which\s+(\w+)\s+(?:of\s+the\s+following\s+)?(?:are\s+|statements?\s+are\s+)correct', 0.85),
            (r'which\s+(?:of\s+the\s+following\s+)?(\w+)\s+statements?\s+are\s+true', 0.85),
            
            # Question patterns that suggest multiple answers
            (r'what\s+are\s+the\s+(\w+)', 0.70),
            (r'which\s+ones?\s+are', 0.75),
            
            # Checkbox indicators in options
            (r'\[\s*\]\s*', 0.60),  # Empty checkboxes
            (r'☐', 0.80),  # Checkbox unicode
            (r'□', 0.80),  # Empty square unicode
        ]
        
        # Enhanced number word to digit mapping
        self.number_words = {
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
            'all': 99,  # Special case for "select all"
            'any': 99,  # "any that apply"
            'multiple': 99  # "multiple answers"
        }
    
    def detect_file_format(self, file_path):
        """Enhanced format detection with multiple fallback strategies"""
        file_path = Path(file_path)
        
        # 1. File extension check
        if file_path.suffix.lower() == '.json':
            logger.debug(f"Format detected by extension: JSON for {file_path.name}")
            return 'json'
        elif file_path.suffix.lower() in ['.html', '.htm']:
            logger.debug(f"Format detected by extension: HTML for {file_path.name}")
            return 'html'
        
        # 2. Content-based detection with enhanced patterns
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # Read more content for better detection
                content = f.read(1000).strip()
                
                # JSON detection patterns
                json_patterns = [
                    r'^\s*[\{\[]',  # Starts with { or [
                    r'"[^"]*"\s*:\s*[\{\[\"]',  # JSON key-value patterns
                    r'^\s*{\s*"[^"]*"',  # Object with quoted keys
                ]
                
                for pattern in json_patterns:
                    if re.search(pattern, content, re.MULTILINE):
                        logger.debug(f"Format detected by content pattern: JSON for {file_path.name}")
                        return 'json'
                
                # HTML detection patterns
                html_patterns = [
                    r'<!DOCTYPE\s+html',
                    r'<html[^>]*>',
                    r'<head[^>]*>',
                    r'<body[^>]*>',
                    r'<div[^>]*>',
                    r'<script[^>]*>',
                    r'let\s+data\s*=',  # Common in our exam HTML files
                    r'var\s+data\s*=',
                    r'const\s+data\s*='
                ]
                
                for pattern in html_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        logger.debug(f"Format detected by content pattern: HTML for {file_path.name}")
                        return 'html'
                
                # 3. Hybrid detection for embedded JSON in HTML
                if re.search(r'<.*>.*[\{\[].*<.*>', content, re.DOTALL):
                    logger.debug(f"Format detected as HTML with embedded data for {file_path.name}")
                    return 'html'
                
                # 4. Fallback: try parsing as JSON
                try:
                    json.loads(content)
                    logger.debug(f"Format detected by JSON parsing: JSON for {file_path.name}")
                    return 'json'
                except json.JSONDecodeError:
                    pass
                
                logger.warning(f"Could not detect format for {file_path.name}, defaulting to HTML")
                return 'html'  # Default fallback
                
        except Exception as e:
            logger.error(f"Error detecting format for {file_path}: {e}")
            # Final fallback based on common patterns in filename
            if 'json' in file_path.name.lower():
                return 'json'
            else:
                return 'html'
    
    def extract_data_from_html(self, html_file_path):
        """Extract JSON data from HTML file"""
        try:
            with open(html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Try multiple extraction patterns
            patterns = [
                r'let data = ({.*?});',
                r'var data = ({.*?});',
                r'const data = ({.*?});',
                r'data\s*=\s*({.*?});'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, html_content, re.DOTALL)
                if match:
                    return json.loads(match.group(1))
            
            raise ValueError("No JSON data pattern found in HTML file")
            
        except Exception as e:
            logger.error(f"Error extracting from HTML {html_file_path}: {e}")
            return None
    
    def extract_data_from_json(self, json_file_path):
        """Extract data from JSON file"""
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading JSON {json_file_path}: {e}")
            return None
    
    def detect_multi_answer_requirement(self, question_text, options=None):
        """Enhanced automatic detection of multi-answer requirements with confidence scoring"""
        text_lower = question_text.lower()
        
        # Track best match and confidence
        best_match = None
        highest_confidence = 0.0
        detected_count = 1
        
        # 1. Pattern-based detection with confidence scoring
        for pattern, confidence in self.multi_answer_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match and confidence > highest_confidence:
                highest_confidence = confidence
                best_match = match
                
                # Extract number if pattern includes capture group
                if match.groups():
                    number_word = match.group(1).lower()
                    detected_count = self.number_words.get(number_word, 1)
                else:
                    # Patterns without capture groups (like "mark all that apply")
                    detected_count = 99
        
        # 2. Option-based analysis if available
        option_confidence = 0.0
        if options:
            checkbox_indicators = 0
            radio_indicators = 0
            
            for option in options:
                option_text = str(option).lower()
                # Count checkbox vs radio indicators
                if any(indicator in option_text for indicator in ['[]', '☐', '□']):
                    checkbox_indicators += 1
                elif any(indicator in option_text for indicator in ['()', '○', '◯']):
                    radio_indicators += 1
            
            if checkbox_indicators > radio_indicators:
                option_confidence = 0.70
                if detected_count == 1:  # Override if options suggest multi-select
                    detected_count = 2  # Conservative default
        
        # 3. Structural analysis
        structural_confidence = 0.0
        
        # Look for plural forms suggesting multiple answers
        plural_patterns = [
            r'which\s+(?:of\s+the\s+following\s+)?(?:statements?|options?|items?)\s+are',
            r'what\s+are\s+the',
            r'identify\s+the\s+(?:correct\s+)?(?:statements?|options?)',
            r'select\s+(?:the\s+)?(?:correct\s+)?(?:statements?|options?)'
        ]
        
        for pattern in plural_patterns:
            if re.search(pattern, text_lower):
                structural_confidence = 0.60
                if detected_count == 1:
                    detected_count = 2
                break
        
        # 4. Final confidence calculation
        final_confidence = max(highest_confidence, option_confidence, structural_confidence)
        
        # 5. Determine question type
        if detected_count > 1 or final_confidence >= 0.70:
            question_type = "multi-select"
            required_answers = detected_count if detected_count < 99 else len(options) if options else 2
            
            logger.info(f"Multi-answer detected: requires {required_answers} answers (confidence: {final_confidence:.2f})")
            
            # Log detection details for debugging
            if best_match:
                logger.debug(f"Pattern matched: '{best_match.group()}' with confidence {highest_confidence}")
            if option_confidence > 0:
                logger.debug(f"Option analysis confidence: {option_confidence}")
            if structural_confidence > 0:
                logger.debug(f"Structural analysis confidence: {structural_confidence}")
                
            return {
                "type": question_type,
                "required_answers": required_answers,
                "confidence": final_confidence,
                "detection_method": "pattern" if highest_confidence == final_confidence else "structural"
            }
        else:
            return {
                "type": "single-select", 
                "required_answers": 1,
                "confidence": 1.0 - final_confidence,  # Confidence in single-select
                "detection_method": "default"
            }
    
    def validate_exam_data(self, exam_data, source_file):
        """Comprehensive validation of extracted exam data"""
        validation_errors = []
        
        if not exam_data:
            validation_errors.append("No data extracted from file")
            return False, validation_errors
        
        # Check for required top-level fields
        if 'questions' not in exam_data:
            validation_errors.append("Missing 'questions' field in exam data")
        
        questions = exam_data.get('questions', [])
        if not questions:
            validation_errors.append("No questions found in exam data")
            return False, validation_errors
        
        # Validate each question
        for i, question in enumerate(questions):
            q_errors = self._validate_question(question, i)
            validation_errors.extend(q_errors)
        
        # Log validation results
        if validation_errors:
            logger.warning(f"Validation issues found in {source_file}: {len(validation_errors)} errors")
            for error in validation_errors[:5]:  # Log first 5 errors
                logger.warning(f"  - {error}")
            if len(validation_errors) > 5:
                logger.warning(f"  ... and {len(validation_errors) - 5} more errors")
        else:
            logger.info(f"✅ Validation passed for {source_file}")
        
        # Allow processing with warnings, but fail if critical errors
        critical_errors = [e for e in validation_errors if 'critical' in e.lower()]
        return len(critical_errors) == 0, validation_errors
    
    def _validate_question(self, question, index):
        """Validate individual question structure"""
        errors = []
        
        # Required fields
        if not question.get('question'):
            errors.append(f"Question {index}: Missing question text")
        
        if 'options' not in question:
            errors.append(f"Question {index}: Missing options")
        elif not question['options']:
            errors.append(f"Question {index}: Empty options list")
        elif len(question['options']) < 2:
            errors.append(f"Question {index}: Insufficient options (need at least 2)")
        
        # Check for question ID
        if not question.get('id'):
            errors.append(f"Question {index}: Missing question ID")
        
        return errors
    
    def check_for_duplicates(self, session, exam_title, original_id):
        """Check if exam or question already exists"""
        from src.models import Exam, Question
        
        # Check for existing exam
        if exam_title:
            existing_exam = session.query(Exam).filter(Exam.title == exam_title).first()
            if existing_exam:
                return 'exam', existing_exam
        
        # Check for existing question
        if original_id:
            existing_question = session.query(Question).filter(Question.original_id == str(original_id)).first()
            if existing_question:
                return 'question', existing_question
                
        return None, None
    
    def process_single_file(self, file_path, session):
        """Process a single exam file (HTML or JSON)"""
        try:
            logger.info(f"Processing file: {file_path}")
            
            # Detect format and extract data
            file_format = self.detect_file_format(file_path)
            
            if file_format == 'html':
                exam_data = self.extract_data_from_html(file_path)
            else:
                exam_data = self.extract_data_from_json(file_path)
            
            if not exam_data:
                logger.error(f"Failed to extract data from {file_path}")
                self.stats['errors'] += 1
                return False
            
            # Validate extracted data
            is_valid, validation_errors = self.validate_exam_data(exam_data, file_path)
            if not is_valid:
                logger.error(f"Validation failed for {file_path}: {len(validation_errors)} critical errors")
                self.stats['errors'] += 1
                return False
            
            # Import to database
            success = self.import_exam_to_database(exam_data, session, file_path)
            
            if success:
                self.stats['files_processed'] += 1
                logger.info(f"✅ Successfully processed {file_path}")
            else:
                self.stats['errors'] += 1
                logger.error(f"❌ Failed to import {file_path}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            self.stats['errors'] += 1
            return False
    
    def import_exam_to_database(self, exam_data, session, source_file):
        """Import exam data with duplicate checking and metadata detection"""
        from src.models import Exam, Question, Answer
        from src.models.module import Module, Topic
        
        try:
            # Generate exam title from source file
            exam_title = f"PCEP Exam - {Path(source_file).stem}"
            
            # Check for duplicate exam
            duplicate_type, duplicate_obj = self.check_for_duplicates(session, exam_title, None)
            if duplicate_type == 'exam':
                logger.warning(f"Exam already exists: {exam_title}")
                self.stats['skipped_duplicates'] += 1
                return True
            
            # Create or get module and topic
            module = session.query(Module).filter(Module.name == "Python Fundamentals").first()
            if not module:
                module = Module(
                    name="Python Fundamentals",
                    description="PCEP certification exam content",
                    display_order=1
                )
                session.add(module)
                session.flush()
            
            topic = session.query(Topic).filter(Topic.name == "Python Fundamentals").first()
            if not topic:
                topic = Topic(
                    name="Python Fundamentals",
                    description="Core Python programming concepts",
                    module_id=module.id,
                    display_order=1
                )
                session.add(topic)
                session.flush()
            
            # Create exam
            exam = Exam(
                title=exam_title,
                description=f"Imported from {Path(source_file).name}",
                time_limit=exam_data.get('timeLimitInMinutes', 30),
                total_questions=len(exam_data.get('questions', [])),
                source_file=Path(source_file).name,
                version="1.0",
                is_active=True
            )
            session.add(exam)
            session.flush()
            self.stats['exams_created'] += 1
            
            # Process questions
            for q_data in exam_data.get('questions', []):
                # Check for duplicate question
                duplicate_type, duplicate_obj = self.check_for_duplicates(session, None, q_data.get('id'))
                if duplicate_type == 'question':
                    logger.warning(f"Question {q_data.get('id')} already exists, skipping")
                    self.stats['skipped_duplicates'] += 1
                    continue
                
                # Detect multi-answer requirement with enhanced analysis
                question_text = q_data.get('question', '')
                options = q_data.get('options', [])
                metadata = self.detect_multi_answer_requirement(question_text, options)
                
                # Create question
                question = Question(
                    original_id=str(q_data.get('id', '')),
                    text=question_text,
                    html_content=question_text,
                    difficulty=q_data.get('difficulty', 1),
                    topic_id=topic.id,
                    exam_id=exam.id,
                    explanation=q_data.get('explanation', 'Imported from exam data'),
                    question_order=self.stats['questions_imported'] + 1,
                    question_metadata=json.dumps(metadata)
                )
                session.add(question)
                session.flush()
                self.stats['questions_imported'] += 1
                
                # Create answers
                options = q_data.get('options', [])
                for i, option in enumerate(options):
                    option_text = option.get('option', option) if isinstance(option, dict) else option
                    
                    answer = Answer(
                        original_id=f"{q_data.get('id')}_{i}",
                        text=option_text,
                        html_content=option_text,
                        is_correct=False,  # Will be updated based on correct answers
                        question_id=question.id,
                        answer_order=i + 1
                    )
                    session.add(answer)
                    self.stats['answers_imported'] += 1
            
            session.commit()
            logger.info(f"✅ Imported {exam.title} with {len(exam_data.get('questions', []))} questions")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Database import error: {e}")
            return False
    
    def process_all_datasets(self):
        """Process all exam datasets in batch"""
        logger.info("🚀 Starting batch processing of all exam datasets")
        
        # Initialize database
        from src.app import create_app
        from src.database import init_database
        
        app = create_app()
        
        with app.app_context():
            # Get database session using the app's database manager
            session = app.db_manager.get_session()
            
            try:
                # Process HTML files
                html_dir = Path("Exam_HTML_Raw_Data")
                if html_dir.exists():
                    logger.info(f"Processing HTML files from {html_dir}")
                    for html_file in html_dir.glob("*.html"):
                        self.process_single_file(str(html_file), session)
                else:
                    logger.warning(f"HTML directory not found: {html_dir}")
                
                # Process JSON files
                json_dir = Path("Exam_Raw_Data_JSON")
                if json_dir.exists():
                    logger.info(f"Processing JSON files from {json_dir}")
                    for json_file in json_dir.glob("*.json"):
                        self.process_single_file(str(json_file), session)
                else:
                    logger.warning(f"JSON directory not found: {json_dir}")
                
                session.close()
                
                # Print final statistics
                self.print_summary()
                
            except Exception as e:
                session.rollback()
                session.close()
                logger.error(f"Batch processing failed: {e}")
                raise
    
    def print_summary(self):
        """Print processing summary"""
        print("\n" + "="*50)
        print("📊 BATCH PROCESSING SUMMARY")
        print("="*50)
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"Exams created: {self.stats['exams_created']}")
        print(f"Questions imported: {self.stats['questions_imported']}")
        print(f"Answers imported: {self.stats['answers_imported']}")
        print(f"Duplicates skipped: {self.stats['skipped_duplicates']}")
        print(f"Errors: {self.stats['errors']}")
        print("="*50)

def main():
    """Main entry point"""
    converter = RobustExamConverter()
    converter.process_all_datasets()

if __name__ == "__main__":
    main()

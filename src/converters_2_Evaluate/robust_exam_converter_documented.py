#!/usr/bin/env python3
"""
ROBUST Multi-Dataset Converter for PCEP Exam Data
==================================================

OVERVIEW:
---------
This converter is designed to process multiple types of exam data files (HTML, JSON) 
and import them into a SQLAlchemy database for the PCEP Exam Practice System. It features 
intelligent format detection, multi-answer question handling, duplicate prevention, 
and comprehensive error handling.

HOW IT WORKS:
-------------
1. **Format Detection**: Automatically detects whether input files are HTML or JSON
   - Uses file extensions (.html, .json) as primary indicator
   - Falls back to content analysis using regex patterns
   - Can handle HTML files with embedded JavaScript data objects

2. **Data Extraction**: 
   - HTML: Extracts JavaScript data objects (let data = {...}, var data = {...})
   - JSON: Direct JSON parsing with error handling
   - Validates extracted data structure before processing

3. **Multi-Answer Detection**: Intelligently determines if questions require single or multiple answers
   - Pattern-based analysis: "Select two answers", "Mark all that apply"
   - Option analysis: Detects checkbox vs radio button indicators
   - Confidence scoring: Each detection method has a confidence score
   - Structural analysis: Examines question text for plural forms

4. **Database Import**:
   - Creates Exam, Question, and Answer records
   - Handles topic/module assignment
   - Prevents duplicate imports
   - Maintains referential integrity

5. **Error Handling**: Comprehensive validation and error reporting at each step

USAGE EXAMPLES:
---------------

Example 1: Process a single HTML file
```python
from robust_exam_converter_documented import RobustExamConverter

converter = RobustExamConverter()

# Initialize database session (requires Flask app context)
from src.app import create_app
app = create_app()
with app.app_context():
    session = app.db_manager.get_session()
    
    # Process single file
    success = converter.process_single_file("exam_data.html", session)
    
    session.close()
```

Example 2: Batch process all exam files
```python
converter = RobustExamConverter()
converter.process_all_datasets()  # Processes all HTML and JSON files
```

Example 3: Check what type of question will be detected
```python
converter = RobustExamConverter()
question_text = "Which of the following are valid Python keywords? (Select two answers)"
options = ["def", "class", "hello", "world"]

result = converter.detect_multi_answer_requirement(question_text, options)
print(f"Type: {result['type']}")  # "multi-select"
print(f"Required answers: {result['required_answers']}")  # 2
print(f"Confidence: {result['confidence']}")  # 0.98
```

EXPECTED INPUT FORMATS:
-----------------------

HTML Format (with embedded JavaScript):
```html
<!DOCTYPE html>
<html>
<script>
let data = {
    "questions": [
        {
            "id": 1,
            "question": "What is Python?",
            "options": ["Language", "Snake", "Tool", "Framework"],
            "correct": 0,
            "explanation": "Python is a programming language"
        }
    ]
};
</script>
</html>
```

JSON Format:
```json
{
    "questions": [
        {
            "id": 1,
            "question": "What is Python?",
            "options": ["Language", "Snake", "Tool", "Framework"],
            "correct": 0,
            "explanation": "Python is a programming language"
        }
    ],
    "timeLimitInMinutes": 30
}
```

DIRECTORY STRUCTURE:
--------------------
The batch processor expects these directories:
```
project_root/
├── Exam_HTML_Raw_Data/          # HTML files with embedded JS data
│   ├── exam1.html
│   ├── exam2.html
│   └── ...
├── Exam_Raw_Data_JSON/          # Pure JSON exam files
│   ├── exam1.json
│   ├── exam2.json
│   └── ...
└── src/
    ├── models/                  # Database models
    ├── app.py                   # Flask application
    └── database.py              # Database configuration
```

MULTI-ANSWER DETECTION EXAMPLES:
---------------------------------
These patterns will be detected as multi-answer questions:

High Confidence (95-99%):
- "Select two answers"
- "Choose three options"
- "Mark all that apply"
- "(Select two)"

Medium Confidence (70-85%):
- "Which statements are correct"
- "What are the benefits"
- Options with checkbox indicators []

Low Confidence (60-70%):
- Structural analysis of plural forms
- Context-based detection

LOGGING AND MONITORING:
-----------------------
The converter creates detailed logs:
- Timestamped log files: converter_YYYYMMDD_HHMMSS.log
- Console output with progress indicators
- Validation warnings and errors
- Processing statistics

ERROR HANDLING:
---------------
Common issues and how they're handled:
1. **File not found**: Skipped with warning
2. **Invalid JSON**: Logged error, file skipped
3. **Missing required fields**: Validation warnings
4. **Database errors**: Transaction rollback, detailed error logging
5. **Duplicate data**: Intelligent duplicate detection and skipping

PERFORMANCE CONSIDERATIONS:
---------------------------
- Batch processing for multiple files
- Transaction management for data integrity
- Memory-efficient file processing
- Duplicate checking to avoid redundant imports

DEPENDENCIES:
-------------
- SQLAlchemy (database ORM)
- Flask (web framework, for app context)
- Python standard library (json, re, logging, pathlib)
- Custom models from src.models

Lessons Learned Integration:
1. Automatic multi-answer detection
2. Proper metadata handling  
3. Duplicate prevention
4. Batch processing
5. Comprehensive error handling

Author: AI Assistant
Version: 2.0.0 (Documented)
Date: 2025-07-30
"""

import sys
import json
import re
import os
from datetime import datetime
import logging
from pathlib import Path

sys.path.insert(0, 'src')

# Setup logging with detailed configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
    handlers=[
        logging.FileHandler(f'converter_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RobustExamConverter:
    """
    Enhanced converter for processing multiple exam datasets with intelligent features.
    
    This class provides comprehensive functionality for:
    - Multi-format file processing (HTML, JSON)
    - Intelligent multi-answer question detection
    - Database import with duplicate prevention
    - Comprehensive validation and error handling
    
    Attributes:
        stats (dict): Processing statistics including files processed, errors, etc.
        multi_answer_patterns (list): Regex patterns for detecting multi-answer questions
        number_words (dict): Mapping of number words to digits for answer counting
    """
    
    def __init__(self):
        """
        Initialize the converter with default configuration.
        
        Sets up:
        - Processing statistics tracking
        - Multi-answer detection patterns with confidence scores
        - Number word to digit mapping
        """
        # Processing statistics for monitoring and reporting
        self.stats = {
            'files_processed': 0,
            'exams_created': 0,
            'questions_imported': 0,
            'answers_imported': 0,
            'errors': 0,
            'skipped_duplicates': 0
        }
        
        # Enhanced multi-answer detection patterns with confidence scoring
        # Format: (regex_pattern, confidence_score)
        # Higher confidence scores (closer to 1.0) indicate stronger indicators
        self.multi_answer_patterns = [
            # Explicit multi-answer instructions (highest confidence)
            (r'select\s+(\w+)\s+(?:of\s+the\s+)?(?:correct\s+)?answers?', 0.95),
            (r'choose\s+(\w+)\s+(?:of\s+the\s+)?(?:correct\s+)?answers?', 0.95),
            (r'pick\s+(\w+)\s+(?:of\s+the\s+)?(?:correct\s+)?answers?', 0.90),
            (r'mark\s+(\w+)\s+(?:of\s+the\s+)?(?:correct\s+)?answers?', 0.90),
            (r'identify\s+(\w+)\s+(?:correct\s+)?answers?', 0.85),
            
            # Parenthetical instructions (very high confidence)
            (r'\(\s*select\s+(\w+)\s*\)', 0.98),
            (r'\(\s*choose\s+(\w+)\s*\)', 0.98),
            (r'\(\s*mark\s+(\w+)\s*\)', 0.95),
            
            # "All that apply" patterns (highest confidence)
            (r'mark\s+all\s+that\s+apply', 0.99),
            (r'select\s+all\s+that\s+apply', 0.99),
            (r'choose\s+all\s+that\s+apply', 0.99),
            (r'identify\s+all\s+that\s+apply', 0.95),
            
            # Multiple options patterns (medium-high confidence)
            (r'which\s+(\w+)\s+(?:of\s+the\s+following\s+)?(?:are\s+|statements?\s+are\s+)correct', 0.85),
            (r'which\s+(?:of\s+the\s+following\s+)?(\w+)\s+statements?\s+are\s+true', 0.85),
            
            # Question patterns that suggest multiple answers (medium confidence)
            (r'what\s+are\s+the\s+(\w+)', 0.70),
            (r'which\s+ones?\s+are', 0.75),
            
            # Checkbox indicators in options (medium confidence)
            (r'\[\s*\]\s*', 0.60),  # Empty checkboxes
            (r'☐', 0.80),  # Checkbox unicode
            (r'□', 0.80),  # Empty square unicode
        ]
        
        # Enhanced number word to digit mapping for answer counting
        self.number_words = {
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
            'all': 99,  # Special case for "select all"
            'any': 99,  # "any that apply"
            'multiple': 99  # "multiple answers"
        }
    
    def detect_file_format(self, file_path):
        """
        Enhanced format detection with multiple fallback strategies.
        
        Detection strategy:
        1. File extension check (.json, .html, .htm)
        2. Content-based detection using regex patterns
        3. Hybrid detection for HTML with embedded JSON
        4. JSON parsing attempt as final validation
        
        Args:
            file_path (str): Path to the file to analyze
            
        Returns:
            str: Detected format ('json' or 'html')
            
        Example:
            >>> converter = RobustExamConverter()
            >>> format_type = converter.detect_file_format("exam_data.html")
            >>> print(format_type)  # "html"
        """
        file_path = Path(file_path)
        
        # Strategy 1: File extension check (most reliable)
        if file_path.suffix.lower() == '.json':
            logger.debug(f"Format detected by extension: JSON for {file_path.name}")
            return 'json'
        elif file_path.suffix.lower() in ['.html', '.htm']:
            logger.debug(f"Format detected by extension: HTML for {file_path.name}")
            return 'html'
        
        # Strategy 2: Content-based detection with enhanced patterns
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # Read more content for better detection (1KB should be sufficient)
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
                
                # Strategy 3: Hybrid detection for embedded JSON in HTML
                if re.search(r'<.*>.*[\{\[].*<.*>', content, re.DOTALL):
                    logger.debug(f"Format detected as HTML with embedded data for {file_path.name}")
                    return 'html'
                
                # Strategy 4: Fallback - try parsing as JSON
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
        """
        Extract JSON data from HTML file containing embedded JavaScript data.
        
        Looks for common JavaScript data patterns:
        - let data = {...};
        - var data = {...};
        - const data = {...};
        - data = {...};
        
        Args:
            html_file_path (str): Path to HTML file
            
        Returns:
            dict: Extracted JSON data or None if extraction fails
            
        Example:
            >>> converter = RobustExamConverter()
            >>> data = converter.extract_data_from_html("exam.html")
            >>> print(f"Found {len(data['questions'])} questions")
        """
        try:
            with open(html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Try multiple extraction patterns in order of specificity
            patterns = [
                r'let data = ({.*?});',      # Modern ES6 syntax
                r'var data = ({.*?});',      # Traditional JavaScript
                r'const data = ({.*?});',    # Immutable declaration
                r'data\s*=\s*({.*?});'      # Simple assignment
            ]
            
            for pattern in patterns:
                match = re.search(pattern, html_content, re.DOTALL)
                if match:
                    json_str = match.group(1)
                    logger.debug(f"Found data pattern: {pattern[:20]}...")
                    return json.loads(json_str)
            
            raise ValueError("No JSON data pattern found in HTML file")
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error in HTML {html_file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error extracting from HTML {html_file_path}: {e}")
            return None
    
    def extract_data_from_json(self, json_file_path):
        """
        Extract data from pure JSON file.
        
        Args:
            json_file_path (str): Path to JSON file
            
        Returns:
            dict: Parsed JSON data or None if parsing fails
            
        Example:
            >>> converter = RobustExamConverter()
            >>> data = converter.extract_data_from_json("exam.json")
            >>> print(f"Exam has {data.get('timeLimitInMinutes', 30)} minute limit")
        """
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.debug(f"Successfully parsed JSON from {json_file_path}")
                return data
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error in {json_file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error reading JSON {json_file_path}: {e}")
            return None
    
    def detect_multi_answer_requirement(self, question_text, options=None):
        """
        Enhanced automatic detection of multi-answer requirements with confidence scoring.
        
        This is one of the most sophisticated features of the converter. It analyzes
        question text and options to determine if a question requires single or multiple answers.
        
        Detection methods:
        1. Pattern-based: Looks for explicit instructions like "Select two answers"
        2. Option-based: Analyzes option formatting for checkbox vs radio indicators
        3. Structural: Examines grammar and sentence structure for plural forms
        
        Args:
            question_text (str): The question text to analyze
            options (list, optional): List of answer options for additional analysis
            
        Returns:
            dict: Detection result with keys:
                - type: "single-select" or "multi-select"
                - required_answers: Number of required answers (1 for single, 2+ for multi)
                - confidence: Confidence score (0.0 to 1.0)
                - detection_method: Method used for detection
                
        Example:
            >>> converter = RobustExamConverter()
            >>> result = converter.detect_multi_answer_requirement(
            ...     "Which of the following are Python keywords? (Select two)",
            ...     ["def", "class", "hello", "world"]
            ... )
            >>> print(result)
            {
                'type': 'multi-select',
                'required_answers': 2,
                'confidence': 0.98,
                'detection_method': 'pattern'
            }
        """
        text_lower = question_text.lower()
        
        # Track best match and confidence across all detection methods
        best_match = None
        highest_confidence = 0.0
        detected_count = 1  # Default to single answer
        
        # Method 1: Pattern-based detection with confidence scoring
        logger.debug(f"Analyzing question: {question_text[:50]}...")
        
        for pattern, confidence in self.multi_answer_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match and confidence > highest_confidence:
                highest_confidence = confidence
                best_match = match
                
                # Extract number if pattern includes capture group
                if match.groups():
                    number_word = match.group(1).lower()
                    detected_count = self.number_words.get(number_word, 1)
                    logger.debug(f"Found number word: '{number_word}' -> {detected_count}")
                else:
                    # Patterns without capture groups (like "mark all that apply")
                    detected_count = 99  # Special value for "all"
                    logger.debug(f"Found 'all that apply' pattern")
        
        # Method 2: Option-based analysis if available
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
                    logger.debug(f"Option analysis suggests multi-select (checkboxes: {checkbox_indicators})")
        
        # Method 3: Structural analysis
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
                    detected_count = 2  # Conservative default for plural
                    logger.debug(f"Structural analysis suggests multi-select (plural pattern: {pattern})")
                break
        
        # Method 4: Final confidence calculation and decision
        final_confidence = max(highest_confidence, option_confidence, structural_confidence)
        
        # Method 5: Determine question type based on analysis
        if detected_count > 1 or final_confidence >= 0.70:
            question_type = "multi-select"
            # Handle special case where detected_count is 99 (all)
            if detected_count >= 99:
                required_answers = len(options) if options else 2
            else:
                required_answers = detected_count
            
            logger.info(f"✓ Multi-answer detected: requires {required_answers} answers (confidence: {final_confidence:.2f})")
            
            # Log detection details for debugging
            if best_match:
                logger.debug(f"  Pattern matched: '{best_match.group()}' with confidence {highest_confidence}")
            if option_confidence > 0:
                logger.debug(f"  Option analysis confidence: {option_confidence}")
            if structural_confidence > 0:
                logger.debug(f"  Structural analysis confidence: {structural_confidence}")
                
            return {
                "type": question_type,
                "required_answers": required_answers,
                "confidence": final_confidence,
                "detection_method": "pattern" if highest_confidence == final_confidence else "structural"
            }
        else:
            logger.debug(f"Single-answer detected (confidence: {1.0 - final_confidence:.2f})")
            return {
                "type": "single-select", 
                "required_answers": 1,
                "confidence": 1.0 - final_confidence,  # Confidence in single-select
                "detection_method": "default"
            }
    
    def validate_exam_data(self, exam_data, source_file):
        """
        Comprehensive validation of extracted exam data.
        
        Validates:
        - Required top-level fields (questions)
        - Question structure and required fields
        - Data consistency and completeness
        
        Args:
            exam_data (dict): Extracted exam data to validate
            source_file (str): Source file path for error reporting
            
        Returns:
            tuple: (is_valid, validation_errors)
                - is_valid (bool): True if data passes validation
                - validation_errors (list): List of validation error messages
                
        Example:
            >>> converter = RobustExamConverter()
            >>> is_valid, errors = converter.validate_exam_data(exam_data, "exam.html")
            >>> if not is_valid:
            ...     print(f"Validation failed: {len(errors)} errors")
        """
        validation_errors = []
        
        # Check for null/empty data
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
        """
        Validate individual question structure.
        
        Args:
            question (dict): Question data to validate
            index (int): Question index for error reporting
            
        Returns:
            list: List of validation errors for this question
        """
        errors = []
        
        # Required fields validation
        if not question.get('question'):
            errors.append(f"Question {index}: Missing question text")
        
        if 'options' not in question:
            errors.append(f"Question {index}: Missing options")
        elif not question['options']:
            errors.append(f"Question {index}: Empty options list")
        elif len(question['options']) < 2:
            errors.append(f"Question {index}: Insufficient options (need at least 2)")
        
        # Check for question ID (helpful for debugging)
        if not question.get('id'):
            errors.append(f"Question {index}: Missing question ID")
        
        # Additional validation could include:
        # - Check for correct answer specification
        # - Validate option format consistency
        # - Check explanation presence
        
        return errors
    
    def check_for_duplicates(self, session, exam_title, original_id):
        """
        Check if exam or question already exists in database.
        
        This prevents duplicate imports and maintains data integrity.
        
        Args:
            session: SQLAlchemy database session
            exam_title (str): Title of exam to check
            original_id (str): Original ID of question to check
            
        Returns:
            tuple: (duplicate_type, duplicate_object)
                - duplicate_type: 'exam', 'question', or None
                - duplicate_object: Database object if found, None otherwise
                
        Example:
            >>> duplicate_type, obj = converter.check_for_duplicates(session, "PCEP Exam 1", "Q001")
            >>> if duplicate_type:
            ...     print(f"Found duplicate {duplicate_type}")
        """
        from src.models import Exam, Question
        
        # Check for existing exam by title
        if exam_title:
            existing_exam = session.query(Exam).filter(Exam.title == exam_title).first()
            if existing_exam:
                logger.debug(f"Found duplicate exam: {exam_title}")
                return 'exam', existing_exam
        
        # Check for existing question by original ID
        if original_id:
            existing_question = session.query(Question).filter(Question.original_id == str(original_id)).first()
            if existing_question:
                logger.debug(f"Found duplicate question: {original_id}")
                return 'question', existing_question
                
        return None, None
    
    def process_single_file(self, file_path, session):
        """
        Process a single exam file (HTML or JSON) through the complete pipeline.
        
        Pipeline stages:
        1. Format detection
        2. Data extraction
        3. Validation
        4. Database import
        
        Args:
            file_path (str): Path to file to process
            session: SQLAlchemy database session
            
        Returns:
            bool: True if processing successful, False otherwise
            
        Example:
            >>> converter = RobustExamConverter()
            >>> success = converter.process_single_file("exam1.html", session)
            >>> if success:
            ...     print("File processed successfully")
        """
        try:
            logger.info(f"🔄 Processing file: {file_path}")
            
            # Stage 1: Detect format and extract data
            file_format = self.detect_file_format(file_path)
            logger.debug(f"Detected format: {file_format}")
            
            if file_format == 'html':
                exam_data = self.extract_data_from_html(file_path)
            else:
                exam_data = self.extract_data_from_json(file_path)
            
            if not exam_data:
                logger.error(f"❌ Failed to extract data from {file_path}")
                self.stats['errors'] += 1
                return False
            
            logger.debug(f"Extracted {len(exam_data.get('questions', []))} questions")
            
            # Stage 2: Validate extracted data
            is_valid, validation_errors = self.validate_exam_data(exam_data, file_path)
            if not is_valid:
                logger.error(f"❌ Validation failed for {file_path}: {len(validation_errors)} critical errors")
                self.stats['errors'] += 1
                return False
            elif validation_errors:
                logger.warning(f"⚠️ Validation warnings for {file_path}: {len(validation_errors)} issues")
            
            # Stage 3: Import to database
            success = self.import_exam_to_database(exam_data, session, file_path)
            
            if success:
                self.stats['files_processed'] += 1
                logger.info(f"✅ Successfully processed {file_path}")
            else:
                self.stats['errors'] += 1
                logger.error(f"❌ Failed to import {file_path}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error processing {file_path}: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            self.stats['errors'] += 1
            return False
    
    def import_exam_to_database(self, exam_data, session, source_file):
        """
        Import exam data to database with duplicate checking and metadata detection.
        
        Creates:
        - Exam record with metadata
        - Module and Topic if they don't exist
        - Question records with multi-answer detection
        - Answer records linked to questions
        
        Args:
            exam_data (dict): Validated exam data
            session: SQLAlchemy database session
            source_file (str): Source file path for reference
            
        Returns:
            bool: True if import successful, False otherwise
            
        Example:
            >>> success = converter.import_exam_to_database(exam_data, session, "exam.html")
            >>> if success:
            ...     session.commit()
        """
        from src.models import Exam, Question, Answer
        from src.models.module import Module, Topic
        
        try:
            # Generate exam title from source file
            exam_title = f"PCEP Exam - {Path(source_file).stem}"
            logger.debug(f"Creating exam: {exam_title}")
            
            # Check for duplicate exam
            duplicate_type, duplicate_obj = self.check_for_duplicates(session, exam_title, None)
            if duplicate_type == 'exam':
                logger.warning(f"⚠️ Exam already exists: {exam_title}")
                self.stats['skipped_duplicates'] += 1
                return True  # Consider this a success since data already exists
            
            # Create or get module and topic (organizational structure)
            module = session.query(Module).filter(Module.name == "Python Fundamentals").first()
            if not module:
                module = Module(
                    name="Python Fundamentals",
                    description="PCEP certification exam content",
                    display_order=1
                )
                session.add(module)
                session.flush()
                logger.debug("Created new module: Python Fundamentals")
            
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
                logger.debug("Created new topic: Python Fundamentals")
            
            # Create exam record
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
            session.flush()  # Get the exam ID
            self.stats['exams_created'] += 1
            logger.debug(f"Created exam with ID: {exam.id}")
            
            # Process questions
            for i, q_data in enumerate(exam_data.get('questions', [])):
                # Check for duplicate question
                duplicate_type, duplicate_obj = self.check_for_duplicates(session, None, q_data.get('id'))
                if duplicate_type == 'question':
                    logger.warning(f"⚠️ Question {q_data.get('id')} already exists, skipping")
                    self.stats['skipped_duplicates'] += 1
                    continue
                
                # Detect multi-answer requirement with enhanced analysis
                question_text = q_data.get('question', '')
                options = q_data.get('options', [])
                metadata = self.detect_multi_answer_requirement(question_text, options)
                
                # Create question record
                question = Question(
                    original_id=str(q_data.get('id', f'imported_{i}')),
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
                session.flush()  # Get the question ID
                self.stats['questions_imported'] += 1
                logger.debug(f"Created question {question.id}: {question_text[:50]}...")
                
                # Create answer records
                correct_answers = q_data.get('correct', [])
                if not isinstance(correct_answers, list):
                    correct_answers = [correct_answers]  # Handle single correct answer
                
                for j, option in enumerate(options):
                    option_text = option.get('option', option) if isinstance(option, dict) else option
                    
                    answer = Answer(
                        original_id=f"{q_data.get('id', f'imported_{i}')}_{j}",
                        text=option_text,
                        html_content=option_text,
                        is_correct=j in correct_answers,  # Mark correct answers
                        question_id=question.id,
                        answer_order=j + 1
                    )
                    session.add(answer)
                    self.stats['answers_imported'] += 1
                
                logger.debug(f"Created {len(options)} answers for question {question.id}")
            
            # Commit transaction
            session.commit()
            logger.info(f"✅ Imported {exam.title} with {len(exam_data.get('questions', []))} questions")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Database import error: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return False
    
    def process_all_datasets(self):
        """
        Process all exam datasets in batch mode.
        
        Expected directory structure:
        - Exam_HTML_Raw_Data/: HTML files with embedded JavaScript
        - Exam_Raw_Data_JSON/: Pure JSON files
        
        This method:
        1. Initializes Flask application context
        2. Processes all HTML files
        3. Processes all JSON files
        4. Provides comprehensive statistics
        
        Example:
            >>> converter = RobustExamConverter()
            >>> converter.process_all_datasets()
            📊 BATCH PROCESSING SUMMARY
            Files processed: 5
            Exams created: 5
            Questions imported: 120
            ...
        """
        logger.info("🚀 Starting batch processing of all exam datasets")
        
        # Initialize database and Flask application context
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
                    logger.info(f"📂 Processing HTML files from {html_dir}")
                    html_files = list(html_dir.glob("*.html"))
                    logger.info(f"Found {len(html_files)} HTML files")
                    
                    for html_file in html_files:
                        logger.info(f"Processing HTML: {html_file.name}")
                        self.process_single_file(str(html_file), session)
                else:
                    logger.warning(f"⚠️ HTML directory not found: {html_dir}")
                
                # Process JSON files
                json_dir = Path("Exam_Raw_Data_JSON")
                if json_dir.exists():
                    logger.info(f"📂 Processing JSON files from {json_dir}")
                    json_files = list(json_dir.glob("*.json"))
                    logger.info(f"Found {len(json_files)} JSON files")
                    
                    for json_file in json_files:
                        logger.info(f"Processing JSON: {json_file.name}")
                        self.process_single_file(str(json_file), session)
                else:
                    logger.warning(f"⚠️ JSON directory not found: {json_dir}")
                
                session.close()
                
                # Print final statistics
                self.print_summary()
                
            except Exception as e:
                session.rollback()
                session.close()
                logger.error(f"❌ Batch processing failed: {e}")
                import traceback
                logger.error(traceback.format_exc())
                raise
    
    def print_summary(self):
        """
        Print comprehensive processing summary with statistics.
        
        Shows:
        - Files processed successfully
        - Database records created
        - Errors encountered
        - Duplicates skipped
        """
        print("\n" + "="*60)
        print("📊 BATCH PROCESSING SUMMARY")
        print("="*60)
        print(f"✅ Files processed: {self.stats['files_processed']}")
        print(f"📚 Exams created: {self.stats['exams_created']}")
        print(f"❓ Questions imported: {self.stats['questions_imported']}")
        print(f"📝 Answers imported: {self.stats['answers_imported']}")
        print(f"⚠️ Duplicates skipped: {self.stats['skipped_duplicates']}")
        print(f"❌ Errors: {self.stats['errors']}")
        
        # Calculate success rate
        total_attempts = self.stats['files_processed'] + self.stats['errors']
        if total_attempts > 0:
            success_rate = (self.stats['files_processed'] / total_attempts) * 100
            print(f"📈 Success rate: {success_rate:.1f}%")
        
        print("="*60)
        
        # Provide next steps guidance
        if self.stats['errors'] > 0:
            print("\n💡 Next steps:")
            print("- Check the log file for detailed error information")
            print("- Verify file formats and data structure")
            print("- Ensure database connectivity")
        elif self.stats['files_processed'] > 0:
            print("\n🎉 Processing completed successfully!")
            print("- Data is now available in the database")
            print("- You can start the Flask application to view questions")
            print("- Run 'python start_pcep_app.py' to launch the app")

def main():
    """
    Main entry point for standalone execution.
    
    Usage:
        python robust_exam_converter_documented.py
    """
    print("🔄 Robust Exam Converter - Documented Version")
    print("=" * 50)
    
    try:
        converter = RobustExamConverter()
        converter.process_all_datasets()
    except KeyboardInterrupt:
        print("\n⏹️ Processing interrupted by user")
    except Exception as e:
        print(f"\n❌ Processing failed: {e}")
        logger.error(f"Main execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

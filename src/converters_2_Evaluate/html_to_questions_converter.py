#!/usr/bin/env python3
"""
HTML to Questions Converter for PCEP Exam Practice App
=======================================================

This script extracts questions from the PE1 Module 4 Test HTML file,
processes the HTML content, applies syntax highlighting to Python code,
and generates a properly formatted questions dataset for the Flask app.

Features:
- Extracts all questions from embedded JavaScript JSON data
- Parses HTML content and converts to clean text
- Applies Python syntax highlighting using Pygments
- Generates structured question dictionaries
- Creates both the converter script and the questions dataset
- Preserves original question IDs and structure

Usage:
    python html_to_questions_converter.py

Dependencies:
    pip install beautifulsoup4 lxml pygments html2text

Author: PCEP Rapid Practice App Development Team
Version: 1.0
Date: 2025-01-09
"""

import json
import re
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import html

try:
    from bs4 import BeautifulSoup
    from pygments import highlight
    from pygments.lexers import PythonLexer
    from pygments.formatters import HtmlFormatter
    import html2text
except ImportError as e:
    print(f"Missing required dependency: {e}")
    print("Please install dependencies with: pip install beautifulsoup4 lxml pygments html2text")
    exit(1)


class QuestionConverter:
    """Converts HTML quiz data to structured question format with syntax highlighting."""
    
    def __init__(self):
        self.python_lexer = PythonLexer()
        self.html_formatter = HtmlFormatter(
            style='default',
            cssclass='highlight',
            linenos=False,
            noclasses=False
        )
        self.html2text = html2text.HTML2Text()
        self.html2text.ignore_links = True
        self.html2text.ignore_images = True
        
    def extract_javascript_data(self, html_content: str) -> Optional[Dict]:
        """Extract the JavaScript data object containing quiz questions."""
        # Find the data object in the JavaScript
        pattern = r'let data = ({.*?});'
        match = re.search(pattern, html_content, re.DOTALL)
        
        if not match:
            print("Could not find JavaScript data object in HTML")
            return None
            
        data_str = match.group(1)
        
        try:
            # Parse the JavaScript object as JSON
            data = json.loads(data_str)
            return data
        except json.JSONDecodeError as e:
            print(f"Error parsing JavaScript data: {e}")
            return None
    
    def clean_html_content(self, html_content: str) -> str:
        """Clean HTML content and convert to readable text."""
        if not html_content:
            return ""
            
        # Decode HTML entities
        content = html.unescape(html_content)
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')
        
        # Convert to text using html2text for better formatting
        text = self.html2text.handle(str(soup))
        
        # Clean up excessive whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = text.strip()
        
        return text
    
    def extract_and_highlight_code(self, text: str) -> tuple:
        """Extract Python code blocks and apply syntax highlighting."""
        # Pattern to match code blocks (looking for common Python patterns)
        code_patterns = [
            r'```python\n(.*?)\n```',
            r'```\n(.*?)\n```',
            r'`([^`]*(?:def|print|if|for|while|try|except|import|class)[^`]*)`',
            # Match multi-line code that looks like Python
            r'([a-zA-Z_][a-zA-Z0-9_]*\s*=.*?\n(?:[a-zA-Z_][a-zA-Z0-9_]*.*?\n)*)',
        ]
        
        highlighted_text = text
        code_blocks = []
        
        # Look for code patterns and highlight them
        for pattern in code_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
            for match in matches:
                code_content = match.group(1)
                
                # Skip if it's too short or doesn't look like Python
                if len(code_content.strip()) < 3:
                    continue
                    
                # Check if it looks like Python code
                if any(keyword in code_content for keyword in ['def ', 'print(', 'if ', 'for ', 'while ', 'try:', 'except', '=', 'return']):
                    try:
                        # Apply syntax highlighting
                        highlighted_code = highlight(code_content, self.python_lexer, self.html_formatter)
                        code_blocks.append({
                            'original': code_content,
                            'highlighted': highlighted_code
                        })
                        
                        # Replace in text with placeholder
                        placeholder = f"[CODE_BLOCK_{len(code_blocks)-1}]"
                        highlighted_text = highlighted_text.replace(match.group(0), placeholder)
                    except Exception as e:
                        print(f"Warning: Could not highlight code block: {e}")
        
        return highlighted_text, code_blocks
    
    def process_question(self, question_data: Dict) -> Dict:
        """Process a single question and format it for our app."""
        question_id = question_data.get('id', 0)
        question_text = question_data.get('question', '')
        question_type = question_data.get('type', 'Single Choice')
        options = question_data.get('options', [])
        
        # Clean and process question text
        clean_question = self.clean_html_content(question_text)
        question_with_highlighting, question_code_blocks = self.extract_and_highlight_code(clean_question)
        
        # Process options
        processed_options = []
        for option in options:
            option_id = option.get('id', 0)
            option_text = option.get('option', '')
            
            clean_option = self.clean_html_content(option_text)
            option_with_highlighting, option_code_blocks = self.extract_and_highlight_code(clean_option)
            
            processed_options.append({
                'id': option_id,
                'text': option_with_highlighting,
                'code_blocks': option_code_blocks
            })
        
        # Determine question format for our app
        is_multiple_choice = question_type == 'Multiple Choice'
        
        return {
            'id': question_id,
            'question': question_with_highlighting,
            'code_blocks': question_code_blocks,
            'options': processed_options,
            'type': 'multiple' if is_multiple_choice else 'single',
            'multiple_choice': is_multiple_choice,
            'explanation': f"This question is from PE1 Module 4 Test, covering Python functions, tuples, dictionaries, and exceptions.",
            'original_data': question_data  # Keep original for reference
        }
    
    def convert_questions(self, html_file_path: str) -> List[Dict]:
        """Convert all questions from the HTML file."""
        print(f"Reading HTML file: {html_file_path}")
        
        try:
            with open(html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
        except Exception as e:
            print(f"Error reading HTML file: {e}")
            return []
        
        # Extract JavaScript data
        data = self.extract_javascript_data(html_content)
        if not data:
            return []
        
        questions = data.get('questions', [])
        print(f"Found {len(questions)} questions in the HTML file")
        
        # Process each question
        processed_questions = []
        for i, question_data in enumerate(questions, 1):
            print(f"Processing question {i}/{len(questions)}...")
            try:
                processed_question = self.process_question(question_data)
                processed_questions.append(processed_question)
            except Exception as e:
                print(f"Error processing question {i}: {e}")
                continue
        
        print(f"Successfully processed {len(processed_questions)} questions")
        return processed_questions
    
    def save_questions_to_file(self, questions: List[Dict], output_path: str):
        """Save the processed questions to a Python file."""
        print(f"Saving questions to: {output_path}")
        
        # Generate the Python file content
        python_content = '''"""
PCEP Module 4 Test Questions Dataset
===================================

Auto-generated from PE1 -- Module 4 Test HTML file.
Contains all questions with Python syntax highlighting and clean formatting.

Generated by: html_to_questions_converter.py
Date: 2025-01-09
Total Questions: {total_questions}
"""

# Pygments CSS for syntax highlighting
PYGMENTS_CSS = """
{pygments_css}
"""

# Complete questions dataset
PCEP_MODULE_4_QUESTIONS = {questions_data}

# Helper function to get questions
def get_all_questions():
    """Return all questions in the dataset."""
    return PCEP_MODULE_4_QUESTIONS

def get_question_by_id(question_id):
    """Get a specific question by ID."""
    for question in PCEP_MODULE_4_QUESTIONS:
        if question['id'] == question_id:
            return question
    return None

def get_question_count():
    """Get the total number of questions."""
    return len(PCEP_MODULE_4_QUESTIONS)

if __name__ == "__main__":
    print(f"PCEP Module 4 Questions Dataset loaded successfully!")
    print(f"Total questions: {{get_question_count()}}")
    print(f"Question IDs: {{[q['id'] for q in PCEP_MODULE_4_QUESTIONS]}}")
'''.format(
            total_questions=len(questions),
            pygments_css=self.html_formatter.get_style_defs('.highlight'),
            questions_data=json.dumps(questions, indent=2, ensure_ascii=False)
        )
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(python_content)
            print(f"Questions dataset saved successfully to {output_path}")
        except Exception as e:
            print(f"Error saving questions file: {e}")


def main():
    """Main function to run the converter."""
    print("PCEP HTML to Questions Converter")
    print("=" * 50)
    
    # Set up paths
    current_dir = Path(__file__).parent
    html_file = current_dir / "Exam_HTML_Raw_Data" / "PE1 -- Module 4 Test_20250610_v1.html"
    output_file = current_dir / "pcep_module_4_questions.py"
    
    # Check if HTML file exists
    if not html_file.exists():
        print(f"Error: HTML file not found at {html_file}")
        print("Please ensure the HTML file is in the correct location.")
        return
    
    # Create converter and process questions
    converter = QuestionConverter()
    questions = converter.convert_questions(str(html_file))
    
    if not questions:
        print("No questions were successfully processed.")
        return
    
    # Save the questions dataset
    converter.save_questions_to_file(questions, str(output_file))
    
    print("\nConversion Summary:")
    print(f"- Input file: {html_file}")
    print(f"- Output file: {output_file}")
    print(f"- Questions processed: {len(questions)}")
    print(f"- Multiple choice questions: {sum(1 for q in questions if q['multiple_choice'])}")
    print(f"- Single choice questions: {sum(1 for q in questions if not q['multiple_choice'])}")
    
    # Show sample question
    if questions:
        print(f"\nSample question (ID: {questions[0]['id']}):")
        sample_q = questions[0]['question'][:100] + "..." if len(questions[0]['question']) > 100 else questions[0]['question']
        print(f"Question: {sample_q}")
        print(f"Options: {len(questions[0]['options'])}")
        print(f"Code blocks: {len(questions[0]['code_blocks'])}")
    
    print("\nConverter completed successfully!")
    print(f"Next step: Run 'python {output_file}' to test the generated dataset.")


if __name__ == "__main__":
    main()

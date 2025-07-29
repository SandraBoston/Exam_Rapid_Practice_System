#!/usr/bin/env python3
"""Simple test version of the converter to debug issues"""

import json
import re
from pathlib import Path

def test_converter():
    print("Starting HTML to Questions Converter Test")
    print("=" * 50)
    
    # Set up paths
    current_dir = Path(__file__).parent
    html_file = current_dir / "Exam_HTML_Raw_Data" / "PE1 -- Module 4 Test_20250610_v1.html"
    
    print(f"Current directory: {current_dir}")
    print(f"Looking for HTML file at: {html_file}")
    print(f"HTML file exists: {html_file.exists()}")
    
    if not html_file.exists():
        print("ERROR: HTML file not found!")
        return
    
    print("Reading HTML file...")
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        print(f"HTML file size: {len(html_content)} characters")
    except Exception as e:
        print(f"Error reading HTML file: {e}")
        return
    
    print("Looking for JavaScript data...")
    # Find the data object in the JavaScript
    pattern = r'let data = ({.*?});'
    match = re.search(pattern, html_content, re.DOTALL)
    
    if not match:
        print("ERROR: Could not find JavaScript data object in HTML")
        return
    
    print("Found JavaScript data object!")
    data_str = match.group(1)
    print(f"Data string length: {len(data_str)} characters")
    
    try:
        # Parse the JavaScript object as JSON
        data = json.loads(data_str)
        print("Successfully parsed JSON data!")
        
        questions = data.get('questions', [])
        print(f"Found {len(questions)} questions")
        
        if questions:
            first_question = questions[0]
            print(f"First question ID: {first_question.get('id', 'N/A')}")
            print(f"First question type: {first_question.get('type', 'N/A')}")
            print(f"First question options: {len(first_question.get('options', []))}")
            
            # Show first few characters of question text
            question_text = first_question.get('question', '')[:100]
            print(f"First question text (first 100 chars): {question_text}...")
        
        print("\nTest completed successfully!")
        
    except json.JSONDecodeError as e:
        print(f"Error parsing JavaScript data: {e}")
        return

if __name__ == "__main__":
    test_converter()

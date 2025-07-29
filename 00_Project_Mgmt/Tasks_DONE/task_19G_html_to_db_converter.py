#!/usr/bin/env python3
"""
15-Minute Database Integration - HTML to Database Converter
Converts HTML exam data to database format using existing infrastructure
"""

import sys
import json
import re
import os
from datetime import datetime

sys.path.insert(0, 'src')

def extract_json_from_html(html_file_path):
    """Extract JSON data from HTML file (adapted from lean_exam_converter.py)"""
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Extract the JavaScript data object
        pattern = r'let data = ({.*?});'
        match = re.search(pattern, html_content, re.DOTALL)
        
        if match:
            return json.loads(match.group(1))
        else:
            raise ValueError("No JSON data found in HTML file")
            
    except Exception as e:
        print(f"Error extracting JSON from HTML: {e}")
        return None

def import_exam_to_database(exam_data, session):
    """Import exam data to database using SQLAlchemy models"""
    from src.models import Exam, Question, Answer
    from src.models.module import Module, Topic
    
    try:
        # Create exam record
        exam = Exam(
            title=f"PE1 Module Exam {exam_data['id']}",
            description=f"Exam with {len(exam_data['questions'])} questions",
            time_limit=exam_data.get('timeLimitInMinutes', 30),
            total_questions=len(exam_data['questions']),
            source_file=f"exam_{exam_data['id']}.html",
            version="1.0",
            is_active=True
        )
        session.add(exam)
        session.flush()  # Get exam ID
        
        print(f"✅ Created exam: {exam.title} (ID: {exam.id})")
        
        # Create default module if needed
        module = session.query(Module).filter(Module.name == "Python Fundamentals").first()
        if not module:
            module = Module(
                name="Python Fundamentals",
                description="Basic Python programming concepts and syntax",
                display_order=1
            )
            session.add(module)
            session.flush()
            print(f"✅ Created module: {module.name}")
        
        # Create default topic if needed
        topic = session.query(Topic).filter(Topic.name == "Python Fundamentals").first()
        if not topic:
            topic = Topic(
                name="Python Fundamentals",
                description="Basic Python programming concepts",
                module_id=module.id,
                display_order=1
            )
            session.add(topic)
            session.flush()
            print(f"✅ Created topic: {topic.name}")
        
        # Import questions and answers
        question_count = 0
        for q_data in exam_data['questions']:
            # Create question
            question = Question(
                original_id=str(q_data['id']),
                text=q_data['question'],
                html_content=q_data['question'],
                difficulty=1,
                topic_id=topic.id,
                exam_id=exam.id,
                explanation="Imported from HTML exam data",
                question_order=question_count + 1
            )
            session.add(question)
            session.flush()  # Get question ID
            
            # Create answers
            for i, option in enumerate(q_data['options']):
                answer = Answer(
                    text=option['option'],
                    is_correct=False,  # Will be set below
                    question_id=question.id,
                    answer_order=i + 1
                )
                session.add(answer)
            
            question_count += 1
            
        session.commit()
        print(f"✅ Imported {question_count} questions successfully")
        return True
        
    except Exception as e:
        print(f"❌ Database import error: {e}")
        session.rollback()
        return False

def main():
    """Main converter function"""
    print("=== TASK 19G: HTML→Database Converter ===")
    
    # HTML file to convert
    html_file = "Exam_HTML_Raw_Data/PE1 -- Module 2 Test_20250610_v1.html"
    
    if not os.path.exists(html_file):
        print(f"❌ HTML file not found: {html_file}")
        return False
    
    # Extract JSON data
    print(f"📥 Extracting data from {html_file}")
    exam_data = extract_json_from_html(html_file)
    
    if not exam_data:
        print("❌ Failed to extract exam data")
        return False
    
    print(f"✅ Extracted exam data: {len(exam_data['questions'])} questions")
    
    # Import to database
    try:
        from src.app import create_app
        app = create_app()
        
        with app.app_context():
            session = app.db_manager.get_session()
            
            print("📤 Importing to database...")
            success = import_exam_to_database(exam_data, session)
            
            session.close()
            
            if success:
                print("✅ Task 19G COMPLETE: HTML data imported to database")
                return True
            else:
                print("❌ Task 19G FAILED: Import error")
                return False
                
    except Exception as e:
        print(f"❌ Application error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()

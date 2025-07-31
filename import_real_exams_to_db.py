#!/usr/bin/env python3
"""
PCEP Real Exam Database Import Script
====================================

Import all successfully processed real exam files into the PCEP database.
This script uses the validated exam data from the robust converter.

Usage: python import_real_exams_to_db.py
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

# Import converter and database components
from src.converters_2_Evaluate.robust_exam_converter_documented import RobustExamConverter
from src.app import create_app
from src.database import init_database, get_session
from src.models.question import Question, Answer
from src.models.exam import Exam

def setup_database_context():
    """Initialize Flask app and database context."""
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/pcep_exam.db'
    
    with app.app_context():
        # Ensure tables exist
        db.create_all()
        return app

def count_existing_questions():
    """Count questions already in database."""
    return Question.query.count()

def import_exam_file(converter, file_path):
    """Import a single exam file to database."""
    try:
        # Extract exam data
        if file_path.suffix.lower() == '.html':
            data = converter.extract_data_from_html(file_path)
        elif file_path.suffix.lower() == '.json':
            data = converter.extract_data_from_json(file_path)
        else:
            print(f"   ❌ Unsupported file format: {file_path}")
            return 0, 0
        
        if not data:
            print(f"   ❌ No data extracted from {file_path.name}")
            return 0, 0
        
        # Validate data
        is_valid, errors = converter.validate_exam_data(data, str(file_path))
        if not is_valid:
            print(f"   ❌ Validation failed for {file_path.name}: {errors}")
            return 0, 0
        
        # Import to database
        questions_imported = 0
        answers_imported = 0
        
        for q_data in data['questions']:
            # Check if question already exists (by text)
            existing_q = Question.query.filter_by(question_text=q_data['question_text']).first()
            if existing_q:
                print(f"   ⚠️  Question already exists: {q_data['question_text'][:50]}...")
                continue
            
            # Create new question
            question = Question(
                question_text=q_data['question_text'],
                question_type=q_data.get('question_type', 'single-choice'),
                difficulty_level=q_data.get('difficulty_level', 'medium'),
                topic=q_data.get('topic', 'General'),
                explanation=q_data.get('explanation', ''),
                source_file=file_path.name
            )
            
            db.session.add(question)
            db.session.flush()  # Get question ID
            questions_imported += 1
            
            # Add answers
            for ans_data in q_data['answers']:
                answer = Answer(
                    question_id=question.id,
                    answer_text=ans_data['text'],
                    is_correct=ans_data['is_correct']
                )
                db.session.add(answer)
                answers_imported += 1
        
        db.session.commit()
        return questions_imported, answers_imported
        
    except Exception as e:
        db.session.rollback()
        print(f"   ❌ Error importing {file_path.name}: {str(e)}")
        return 0, 0

def main():
    """Main import process."""
    print("🚀 IMPORTING REAL PCEP EXAM FILES TO DATABASE")
    print("=" * 60)
    
    # Initialize
    app = setup_database_context()
    converter = RobustExamConverter()
    exam_dir = Path("Exam_HTML_Raw_Data")
    
    with app.app_context():
        # Check initial state
        initial_questions = count_existing_questions()
        print(f"📊 Initial questions in database: {initial_questions}")
        
        # Get all exam files (skip the problematic JSON)
        html_files = list(exam_dir.glob("*.html"))
        json_files = [f for f in exam_dir.glob("*.json") 
                     if f.name != "PCEP_Exam_Module_3_Question_1_Only_raw_data.json"]
        
        all_files = html_files + json_files
        total_files = len(all_files)
        
        print(f"📁 Found {total_files} valid exam files to import")
        print(f"   📄 HTML files: {len(html_files)}")
        print(f"   📄 JSON files: {len(json_files)}")
        print("=" * 60)
        
        # Import each file
        total_questions_imported = 0
        total_answers_imported = 0
        files_processed = 0
        
        for i, file_path in enumerate(all_files, 1):
            print(f"📄 Processing file {i}/{total_files}: {file_path.name}")
            
            questions_imported, answers_imported = import_exam_file(converter, file_path)
            
            if questions_imported > 0:
                print(f"   ✅ Imported {questions_imported} questions, {answers_imported} answers")
                total_questions_imported += questions_imported
                total_answers_imported += answers_imported
                files_processed += 1
            else:
                print(f"   ⚠️  No new questions imported from {file_path.name}")
        
        # Final summary
        final_questions = count_existing_questions()
        
        print("=" * 60)
        print("📊 IMPORT SUMMARY")
        print("=" * 60)
        print(f"📁 Files processed: {files_processed}/{total_files}")
        print(f"📝 New questions imported: {total_questions_imported}")
        print(f"📋 New answers imported: {total_answers_imported}")
        print(f"🗃️  Total questions in database: {final_questions}")
        print(f"📈 Questions added this session: {final_questions - initial_questions}")
        
        if files_processed == total_files:
            print("✅ All exam files successfully imported!")
        else:
            print(f"⚠️  {total_files - files_processed} files had issues or duplicates")
        
        print("\n💡 Next steps:")
        print("   1. Run the Flask app to test the new questions")
        print("   2. Verify question display and answering functionality")
        print("   3. Check for any data quality issues")

if __name__ == "__main__":
    main()

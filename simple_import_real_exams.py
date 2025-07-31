#!/usr/bin/env python3
"""
Simple Real Exam Database Import Script
======================================

Import processed real exam files into the PCEP database using the existing structure.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.append('src')

from converters_2_Evaluate.robust_exam_converter_documented import RobustExamConverter
from database import init_database
from models.question import Question, Answer
from models.exam import Exam

def main():
    """Main import process."""
    print("🚀 IMPORTING REAL PCEP EXAM FILES TO DATABASE")
    print("=" * 60)
    
    # Initialize database
    db_manager = init_database()
    session = db_manager.get_session()
    converter = RobustExamConverter()
    exam_dir = Path("Exam_HTML_Raw_Data")
    
    try:
        # Check initial state
        initial_questions = session.query(Question).count()
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
        
        # Create a default exam if none exists
        default_exam = session.query(Exam).first()
        if not default_exam:
            default_exam = Exam(title="PCEP Practice Exam", description="Imported questions")
            session.add(default_exam)
            session.commit()
            print(f"📋 Created default exam: {default_exam.title}")
        
        # Import each file
        total_questions_imported = 0
        total_answers_imported = 0
        files_processed = 0
        
        for i, file_path in enumerate(all_files, 1):
            print(f"📄 Processing file {i}/{total_files}: {file_path.name}")
            
            try:
                # Extract exam data
                if file_path.suffix.lower() == '.html':
                    data = converter.extract_data_from_html(file_path)
                elif file_path.suffix.lower() == '.json':
                    data = converter.extract_data_from_json(file_path)
                else:
                    print(f"   ❌ Unsupported file format: {file_path}")
                    continue
                
                if not data:
                    print(f"   ❌ No data extracted from {file_path.name}")
                    continue
                
                # Validate data
                is_valid, errors = converter.validate_exam_data(data, str(file_path))
                if not is_valid:
                    print(f"   ❌ Validation failed for {file_path.name}: {errors}")
                    continue
                
                # Import questions
                questions_imported = 0
                answers_imported = 0
                
                for q_data in data['questions']:
                    # Check if question already exists (by text similarity)
                    question_text = q_data['question']  # Use 'question' not 'question_text'
                    existing_q = session.query(Question).filter(Question.text == question_text).first()
                    
                    if existing_q:
                        print(f"   ⚠️  Duplicate question skipped: {question_text[:50]}...")
                        continue
                    
                    # Create new question (adapt to current schema)
                    question = Question(
                        text=question_text,
                        html_content=question_text,  # Store as HTML content too
                        difficulty=2,  # Default medium difficulty
                        exam_id=default_exam.id,
                        explanation=q_data.get('explanation', ''),
                        question_metadata=f'{{"source_file": "{file_path.name}"}}'
                    )
                    
                    session.add(question)
                    session.flush()  # Get question ID
                    questions_imported += 1
                    
                    # Add answers - handle the correct answer format
                    options = q_data['options']
                    correct_index = q_data['correct']
                    
                    for i, option_text in enumerate(options):
                        answer = Answer(
                            question_id=question.id,
                            text=option_text,
                            is_correct=(i == correct_index)  # True if this is the correct answer
                        )
                        session.add(answer)
                        answers_imported += 1
                
                session.commit()
                
                if questions_imported > 0:
                    print(f"   ✅ Imported {questions_imported} questions, {answers_imported} answers")
                    total_questions_imported += questions_imported
                    total_answers_imported += answers_imported
                    files_processed += 1
                else:
                    print(f"   ⚠️  No new questions imported from {file_path.name}")
                    
            except Exception as e:
                session.rollback()
                print(f"   ❌ Error importing {file_path.name}: {str(e)}")
                continue
        
        # Final summary
        final_questions = session.query(Question).count()
        
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
        
    finally:
        session.close()

if __name__ == "__main__":
    main()

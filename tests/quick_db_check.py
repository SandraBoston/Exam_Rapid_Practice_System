#!/usr/bin/env python3
"""
Quick verification of database question and exam counts
"""
import os
import sys
from pathlib import Path

# Set up paths
project_root = Path(__file__).parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

# Set database path
os.environ['DATABASE_URL'] = f"sqlite:///{project_root}/instance/pcep_exam.db"

try:
    from app import create_app
    from models.exam_models import Exam, Question
    from database import DatabaseManager
    
    app = create_app()
    
    with app.app_context():
        db_manager = DatabaseManager()
        session = db_manager.get_session()
        
        # Count questions and exams
        total_questions = session.query(Question).count()
        total_exams = session.query(Exam).count()
        
        print(f"🔍 DATABASE VERIFICATION")
        print(f"=" * 40)
        print(f"📊 Total Questions: {total_questions}")
        print(f"📚 Total Exams: {total_exams}")
        print()
        
        # Show breakdown by exam
        print(f"📋 EXAM BREAKDOWN:")
        exams = session.query(Exam).all()
        total_questions_check = 0
        for exam in exams:
            question_count = len(exam.questions)
            total_questions_check += question_count
            print(f"  - {exam.name} ({exam.file_type}): {question_count} questions")
        
        print()
        print(f"✅ Verification: {total_questions_check} questions total")
        
        session.close()
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

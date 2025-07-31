import os
import sys
sys.path.insert(0, 'src')
os.environ['DATABASE_URL'] = 'sqlite:///instance/pcep_exam.db'

from src.app import create_app
from src.models.exam_models import Exam, Question

app = create_app()

with app.app_context():
    from src.database import DatabaseManager
    db = DatabaseManager()
    session = db.get_session()
    
    exams = session.query(Exam).all()
    questions = session.query(Question).all()
    
    print(f"🎯 DATABASE VERIFICATION RESULTS")
    print(f"=" * 50)
    print(f"Total exams in database: {len(exams)}")
    print(f"Total questions in database: {len(questions)}")
    print()
    
    print("📋 EXAM DETAILS:")
    for exam in exams:
        print(f"- {exam.name} ({exam.file_type}) - {len(exam.questions)} questions, External ID: {exam.exam_external_id}")
    
    session.close()

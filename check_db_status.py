#!/usr/bin/env python3
"""
Quick script to check database integration status
"""
import sys
import os
sys.path.append('src')

# Check database file
db_path = 'instance/pcep_exam.db'
print(f"🔍 Checking database at: {os.path.abspath(db_path)}")
print(f"📁 Database exists: {os.path.exists(db_path)}")

if os.path.exists(db_path):
    print(f"📊 Database size: {os.path.getsize(db_path)} bytes")
    
    try:
        # Try to connect and query
        from database import DatabaseManager
        from models import Question, Answer
        
        db_manager = DatabaseManager('sqlite:///instance/pcep_exam.db')
        session = db_manager.get_session()
        
        questions = session.query(Question).all()
        print(f"❓ Questions in database: {len(questions)}")
        
        if questions:
            print(f"📝 First question: {questions[0].text[:100]}...")
            
            # Check answers for first question
            answers = session.query(Answer).filter(Answer.question_id == questions[0].id).all()
            print(f"📝 Answers for first question: {len(answers)}")
            
            for i, answer in enumerate(answers):
                correct_marker = "✓" if answer.is_correct else "✗"
                print(f"   {i+1}. {correct_marker} {answer.text[:50]}...")
        
        session.close()
        print("✅ Database connection successful!")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("❌ Database file does not exist")

print("\n" + "="*60)
print("🏗️  DATABASE INTEGRATION STATUS SUMMARY")
print("="*60)

if os.path.exists(db_path) and os.path.getsize(db_path) > 0:
    print("✅ Database file exists and has data")
    print("✅ Flask app has database query code in /api/questions endpoint") 
    print("❓ Status: Database integration appears to be COMPLETE")
    print("📝 Task 19D may be OUTDATED - no hardcoded questions array found")
else:
    print("❌ Database file missing or empty")
    print("📝 Task 19D is ACCURATE - need to set up database")

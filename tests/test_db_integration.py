#!/usr/bin/env python3
"""
Test Database Integration for Flask App
Quick test to verify the database query will work
"""

import os
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def test_database_integration():
    """Test database integration before starting Flask"""
    
    print("🔍 Testing Database Integration...")
    
    try:
        # Import models and database with proper path handling
        import sys
        import os
        sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
        
        from models.question import Question
        from models.question import Answer
        from database import init_database
        
        print("✅ Models imported successfully")
        
        # Initialize database
        db_manager = init_database(database_url='sqlite:///instance/pcep_exam.db')
        print("✅ Database manager initialized")
        
        # Test session creation
        session = db_manager.get_session()
        print("✅ Database session created")
        
        # Test question query
        questions = session.query(Question).all()
        print(f"✅ Found {len(questions)} questions in database")
        
        if len(questions) > 0:
            # Test answer query for first question
            first_question = questions[0]
            answers = session.query(Answer).filter(Answer.question_id == first_question.id).all()
            print(f"✅ First question has {len(answers)} answers")
            
            print(f"\nSample Question:")
            print(f"  ID: {first_question.id}")
            print(f"  Text: {first_question.text[:100]}...")
            print(f"  Answers: {len(answers)}")
            for i, answer in enumerate(answers[:4]):  # Show first 4 answers
                status = "✅ CORRECT" if answer.is_correct else "❌"
                print(f"    {i+1}. {answer.text[:50]}... {status}")
        
        session.close()
        
        print("\n🎯 Database Integration Test: ✅ PASSED")
        print("✅ Flask app should now load questions from database!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Database Integration Test: FAILED")
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_database_integration()
    
    if success:
        print("\n🚀 Ready to start Flask app:")
        print("   start_flask_simple.bat")
        print("   OR: python run_flask_app_fixed.py")
    else:
        print("\n⚠️ Fix database issues before starting Flask app")

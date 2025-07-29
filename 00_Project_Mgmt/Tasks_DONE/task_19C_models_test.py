#!/usr/bin/env python3
"""
15-Minute Database Integration - Task 19C
Test model imports in app context
"""

print('=== TASK 19C: Model Import Test ===')

import sys
sys.path.insert(0, 'src')

try:
    from src.app import create_app
    
    # Create Flask app with model imports
    app = create_app()
    print('✅ Flask app created with model imports')
    
    with app.app_context():
        # Test that models are accessible
        from src.models import User, Question, Answer, Exam
        print('✅ Models imported successfully:')
        print(f'  - User: {User}')
        print(f'  - Question: {Question}')
        print(f'  - Answer: {Answer}')
        print(f'  - Exam: {Exam}')
        
        # Test database session with models
        session = app.db_manager.get_session()
        
        # Test model queries
        question_count = session.query(Question).count()
        print(f'📊 Question.query accessible: {question_count} questions')
        
        session.close()
        
    print('✅ Task 19C COMPLETE: Models integrated in app')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()

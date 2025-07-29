#!/usr/bin/env python3
"""
Task 19I Debug: Check Flask app database connection
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_flask_database():
    print("=== TASK 19I DEBUG: Flask Database Connection ===")
    
    try:
        from src.app import create_app
        
        app = create_app()
        
        with app.app_context():
            print("✅ Flask app created successfully")
            
            # Check if app has database manager
            if hasattr(app, 'db_manager'):
                print("✅ App has db_manager")
                
                session = app.db_manager.get_session()
                print("✅ Database session created")
                
                # Try to query questions directly
                from src.models import Question
                questions = session.query(Question).all()
                print(f"✅ Direct query found {len(questions)} questions")
                
                if questions:
                    first_q = questions[0]
                    print(f"   Sample: {first_q.text[:50]}...")
                    print(f"   Answers: {len(first_q.answers)}")
                
                session.close()
            else:
                print("❌ App missing db_manager")
            
            # Test the actual endpoint
            with app.test_client() as client:
                print("\n🌐 Testing endpoint directly...")
                response = client.get('/api/questions')
                print(f"Status: {response.status_code}")
                
                if response.data:
                    data = response.get_json()
                    print(f"Response data: {data}")
                else:
                    print("No response data")
                    
    except Exception as e:
        print(f"❌ Debug error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_flask_database()

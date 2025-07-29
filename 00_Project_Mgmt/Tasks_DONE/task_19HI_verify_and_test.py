#!/usr/bin/env python3
"""
Task 19H: Verify Database Import Success
Task 19I: Test Application with Database Data
"""

import sqlite3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def task_19H_verify_data():
    """Task 19H: Verify that data was imported correctly"""
    print("=== TASK 19H: Database Import Verification ===")
    
    try:
        conn = sqlite3.connect('instance/pcep_exam.db')
        cursor = conn.cursor()
        
        # Check exam count
        cursor.execute("SELECT COUNT(*) FROM exams")
        exam_count = cursor.fetchone()[0]
        print(f"📊 Exams: {exam_count}")
        
        # Check module count
        cursor.execute("SELECT COUNT(*) FROM modules")
        module_count = cursor.fetchone()[0]
        print(f"📊 Modules: {module_count}")
        
        # Check topic count
        cursor.execute("SELECT COUNT(*) FROM topics")
        topic_count = cursor.fetchone()[0]
        print(f"📊 Topics: {topic_count}")
        
        # Check question count
        cursor.execute("SELECT COUNT(*) FROM questions")
        question_count = cursor.fetchone()[0]
        print(f"📊 Questions: {question_count}")
        
        # Check answer count
        cursor.execute("SELECT COUNT(*) FROM answers")
        answer_count = cursor.fetchone()[0]
        print(f"📊 Answers: {answer_count}")
        
        # Sample a few questions
        print("\n🔍 Sample Questions:")
        cursor.execute("""
        SELECT q.id, q.text, COUNT(a.id) as answer_count
        FROM questions q 
        LEFT JOIN answers a ON q.id = a.question_id 
        GROUP BY q.id 
        LIMIT 3
        """)
        
        for row in cursor.fetchall():
            q_id, q_text, a_count = row
            text_preview = q_text[:60] + "..." if len(q_text) > 60 else q_text
            print(f"  Q{q_id}: {text_preview} ({a_count} answers)")
        
        conn.close()
        
        # Verify minimum expected data
        if question_count >= 20 and answer_count >= 60:
            print("\n✅ Task 19H COMPLETE: Database populated successfully!")
            return True
        else:
            print(f"\n❌ Task 19H FAILED: Expected 20+ questions, got {question_count}")
            return False
            
    except Exception as e:
        print(f"❌ Task 19H FAILED: {e}")
        return False

def task_19I_test_application():
    """Task 19I: Test Flask application with database questions"""
    print("\n=== TASK 19I: Application Test with Database ===")
    
    try:
        from src.app import create_app
        
        # Create app instance
        app = create_app()
        
        with app.test_client() as client:
            print("🌐 Testing /api/questions endpoint...")
            
            # Test the questions API endpoint
            response = client.get('/api/questions')
            
            if response.status_code == 200:
                data = response.get_json()
                
                # Check if data is a list of questions (direct array)
                if isinstance(data, list) and len(data) > 0:
                    print(f"✅ API returned {len(data)} questions")
                    
                    # Check first question structure
                    first_q = data[0]
                    expected_fields = ['id', 'question', 'options']
                    
                    if all(field in first_q for field in expected_fields):
                        print("✅ Question structure looks correct")
                        print(f"   Sample: {first_q['question'][:50]}...")
                        print(f"   Options: {len(first_q['options'])} choices")
                        
                        print("\n✅ Task 19I COMPLETE: Application serving database questions!")
                        return True
                    else:
                        print(f"❌ Missing fields in question: {first_q}")
                        return False
                # Check if data has questions key (alternative format)
                elif isinstance(data, dict) and 'questions' in data and len(data['questions']) > 0:
                    print(f"✅ API returned {len(data['questions'])} questions")
                    
                    # Check first question structure
                    first_q = data['questions'][0]
                    expected_fields = ['id', 'question', 'options']
                    
                    if all(field in first_q for field in expected_fields):
                        print("✅ Question structure looks correct")
                        print(f"   Sample: {first_q['question'][:50]}...")
                        print(f"   Options: {len(first_q['options'])} choices")
                        
                        print("\n✅ Task 19I COMPLETE: Application serving database questions!")
                        return True
                    else:
                        print(f"❌ Missing fields in question: {first_q}")
                        return False
                else:
                    print(f"❌ Unexpected API response format: {type(data)}")
                    print(f"   Data preview: {str(data)[:200]}...")
                    return False
            else:
                print(f"❌ API request failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Task 19I FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Run both tasks
    task_19H_success = task_19H_verify_data()
    
    if task_19H_success:
        task_19I_success = task_19I_test_application()
        
        if task_19I_success:
            print("\n🎉 15-MINUTE DATABASE INTEGRATION SUCCESS!")
            print("✅ Tasks 19A-19I all completed successfully")
            print("✅ Database connected and populated")
            print("✅ Flask app serving questions from database")
        else:
            print("\n❌ Database populated but app integration failed")
    else:
        print("\n❌ Database import verification failed")

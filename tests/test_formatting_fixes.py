#!/usr/bin/env python3
"""
Test the fixed formatting - check API metadata and Flask response
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_api_formatting():
    print("=== TESTING API FORMATTING FIXES ===")
    
    try:
        from src.app import create_app
        
        app = create_app()
        
        with app.test_client() as client:
            print("🌐 Testing /api/questions endpoint...")
            response = client.get('/api/questions')
            
            if response.status_code == 200:
                data = response.get_json()
                
                if data and len(data) > 0:
                    print(f"✅ Found {len(data)} questions")
                    
                    # Test specific questions
                    for i, q in enumerate(data):
                        question_type = q.get('type', 'single-select')
                        required_answers = q.get('required_answers', 1)
                        
                        print(f"\nQ{q['id']}: {question_type}")
                        print(f"  Required answers: {required_answers}")
                        print(f"  Preview: {q['question'][:60]}...")
                        
                        # Check for multi-select questions
                        if question_type == 'multi-select':
                            print(f"  ✅ MULTI-SELECT: Requires {required_answers} answers")
                        
                        # Check for code formatting
                        if '<code' in q['question']:
                            print(f"  📝 CODE BLOCK: Contains code formatting")
                    
                    return True
                else:
                    print("❌ No questions returned")
                    return False
            else:
                print(f"❌ API error: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_api_formatting()

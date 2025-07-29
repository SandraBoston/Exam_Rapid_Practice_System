import requests
import json

try:
    print("Testing Question 2 API...")
    response = requests.get('http://localhost:5000/api/questions')
    if response.status_code == 200:
        data = response.json()
        print('✅ API working')
        print(f'Total questions: {len(data)}')
        if len(data) >= 2:
            question2 = data[1]  # Index 1 = Question 2
            print('\nQuestion 2 Data:')
            print(f'ID: {question2["id"]}')
            print(f'Question: {question2["question"]}')
            print(f'Options count: {len(question2["options"])}')
            print('Options:')
            for i, option in enumerate(question2["options"]):
                print(f'  {i}: {option}')
            print(f'Correct: {question2["correct"]}')
            print(f'Correct Answer: {question2["options"][question2["correct"]]}')
        else:
            print('❌ Not enough questions in response')
    else:
        print(f'❌ API error: {response.status_code}')
        print(f'Response: {response.text}')
except requests.exceptions.ConnectionError:
    print('❌ Connection error: Server not running')
    print('Please start the server first with: quickstart.bat')
except Exception as e:
    print(f'❌ Unexpected error: {e}')

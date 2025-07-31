#!/usr/bin/env python3
"""
Quick database check script
"""
import sys
sys.path.append('src')

from database import init_database
from models.question import Question

# Initialize database
db_manager = init_database()
session = db_manager.get_session()

# Count questions
count = session.query(Question).count()
print(f'Current questions in database: {count}')

# Show some sample questions
questions = session.query(Question).limit(3).all()
for i, q in enumerate(questions, 1):
    print(f'{i}. {q.text[:100]}...')

session.close()

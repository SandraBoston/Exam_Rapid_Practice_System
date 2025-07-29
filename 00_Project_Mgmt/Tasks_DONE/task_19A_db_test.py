#!/usr/bin/env python3
"""
15-Minute Database Integration - Task 19A
Verify database tables exist and are accessible
"""

print('=== TASK 19A: Database Tables Verification ===')

import sqlite3

# Test database access
conn = sqlite3.connect('instance/pcep_exam.db')
cursor = conn.cursor()

# Check tables
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = [row[0] for row in cursor.fetchall()]
print(f'✅ Found {len(tables)} tables: {tables}')

# Check question count
cursor.execute('SELECT count(*) FROM questions')
q_count = cursor.fetchone()[0]
print(f'📊 Questions in database: {q_count}')

# Check exam count  
cursor.execute('SELECT count(*) FROM exams')
e_count = cursor.fetchone()[0]
print(f'📊 Exams in database: {e_count}')

conn.close()
print('✅ Task 19A COMPLETE: Database accessible and ready')

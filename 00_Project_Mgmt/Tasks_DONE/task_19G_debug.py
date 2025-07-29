#!/usr/bin/env python3
"""
Task 19G Debug: Investigate Foreign Key Constraint Error
"""

import sqlite3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_database_schema():
    print("=== TASK 19G DEBUG: Database Schema Analysis ===")
    
    try:
        # Connect to database
        conn = sqlite3.connect('data/pcep_exam.db')
        cursor = conn.cursor()
        
        print("\n📋 Questions Table Schema:")
        cursor.execute('PRAGMA table_info(questions)')
        for row in cursor.fetchall():
            print(f"  {row}")
        
        print("\n📋 Topics Table Contents:")
        cursor.execute('SELECT * FROM topics')
        topics = cursor.fetchall()
        if topics:
            for row in topics:
                print(f"  {row}")
        else:
            print("  ❌ No topics found")
        
        print("\n📋 Exams Table Contents:")
        cursor.execute('SELECT * FROM exams')
        exams = cursor.fetchall()
        if exams:
            for row in exams:
                print(f"  {row}")
        else:
            print("  ❌ No exams found")
        
        print("\n📋 Foreign Key Check:")
        cursor.execute('PRAGMA foreign_key_check')
        fk_errors = cursor.fetchall()
        if fk_errors:
            for error in fk_errors:
                print(f"  ❌ FK Error: {error}")
        else:
            print("  ✅ No foreign key violations")
        
        print("\n📋 Foreign Keys Status:")
        cursor.execute('PRAGMA foreign_keys')
        fk_status = cursor.fetchone()
        print(f"  Foreign keys enabled: {bool(fk_status[0])}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Debug error: {e}")

if __name__ == "__main__":
    debug_database_schema()

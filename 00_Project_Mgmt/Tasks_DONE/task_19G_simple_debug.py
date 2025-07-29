#!/usr/bin/env python3
"""
Task 19G Simple Debug: Check database structure
"""

import sqlite3
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_database():
    print("=== TASK 19G DEBUG: Database Structure Check ===")
    
    # Check if database file exists
    db_path = 'instance/pcep_exam.db'
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        
        # Check if instance directory exists
        if not os.path.exists('instance'):
            print("❌ Instance directory missing - creating it")
            os.makedirs('instance')
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"✅ Connected to {db_path}")
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"📋 Tables: {tables}")
        
        # Check foreign keys
        cursor.execute("PRAGMA foreign_keys")
        fk_status = cursor.fetchone()
        print(f"🔗 Foreign keys enabled: {bool(fk_status[0])}")
        
        # Check existing data
        for table in ['exams', 'topics', 'questions']:
            if table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"📊 {table}: {count} records")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == "__main__":
    check_database()

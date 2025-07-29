#!/usr/bin/env python3
"""
Database Integration Test Script
Tests SQLAlchemy models and session creation for immediate integration
"""

import os
import sys

# Add src to Python path
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

try:
    from database import DatabaseManager
    from models import *
    from sqlalchemy import text
    
    print("=== TESTING DATABASE CONNECTION ===")
    
    # Create database manager
    db_manager = DatabaseManager('sqlite:///instance/pcep_exam.db')
    engine = db_manager.create_engine()
    Session = db_manager.get_session_factory()
    
    print("✅ Database manager created successfully")
    
    # Test session creation
    session = Session()
    print("✅ Database session created successfully")
    
    # Test table existence
    result = session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
    tables = [row[0] for row in result.fetchall()]
    print(f"✅ Found {len(tables)} tables: {tables}")
    
    # Test model imports
    print(f"✅ User model: {User}")
    print(f"✅ Question model: {Question}")  
    print(f"✅ Exam model: {Exam}")
    
    # Test counts
    question_count = session.query(Question).count()
    exam_count = session.query(Exam).count()
    print(f"📊 Questions in database: {question_count}")
    print(f"📊 Exams in database: {exam_count}")
    
    session.close()
    print("✅ Database integration test PASSED")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Need to fix import paths or model issues")
except Exception as e:
    print(f"❌ Database connection error: {e}")
    print("Need to fix database configuration")

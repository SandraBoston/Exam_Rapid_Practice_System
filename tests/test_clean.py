#!/usr/bin/env python3
"""
Clean test script to validate SQLAlchemy ORM configuration for PCEP Exam Accelerator.
"""

import sys
import os
import traceback

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all models can be imported successfully."""
    print("=" * 60)
    print("TESTING IMPORTS")
    print("=" * 60)
    
    try:
        print("Importing database module...")
        from src.database import init_database, DatabaseManager
        print("✅ Database module imported successfully")
        
        print("Importing base models...")
        from src.models import BaseModel, TimestampMixin, JSONMixin
        print("✅ Base models imported successfully")
        
        print("Importing User model...")
        from src.models.user import User
        print("✅ User model imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        traceback.print_exc()
        return False

def test_database_creation():
    """Test database initialization and table creation."""
    print("\n" + "=" * 60)
    print("TESTING DATABASE CREATION")  
    print("=" * 60)
    
    try:
        print("Initializing database manager...")
        from src.database import init_database
        
        # Use test database in memory
        db_manager = init_database(database_url='sqlite:///:memory:', echo=False)
        print("✅ Database manager created successfully")
        print(f"Database URL: {db_manager.database_url}")
        
        print("Creating database tables...")
        db_manager.create_all_tables()
        print("✅ Database tables created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Database creation failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("PCEP Exam Accelerator - SQLAlchemy Configuration Test")
    print("=" * 60)
    
    tests = [test_imports, test_database_creation]
    results = []
    
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for i, (test, result) in enumerate(zip(tests, results), 1):
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"Test {i} ({test.__name__}): {status}")
    
    all_passed = all(results)
    print(f"\nOverall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return all_passed

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
SQLAlchemy Test Script with Logging
Tests the PCEP Exam Accelerator SQLAlchemy implementation and logs all results.
"""

import sys
import traceback
from datetime import datetime
import os

# Create timestamped log file
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = f"sqlalchemy_test_log_{timestamp}.txt"

def log_write(message):
    """Write message to both console and log file"""
    print(message)
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"{datetime.now().isoformat()}: {message}\n")

def test_step(step_name, test_func):
    """Execute a test step and log results"""
    log_write(f"\n{'='*60}")
    log_write(f"TESTING: {step_name}")
    log_write(f"{'='*60}")
    
    try:
        result = test_func()
        log_write(f"✅ SUCCESS: {step_name}")
        if result:
            log_write(f"Result: {result}")
        return True
    except Exception as e:
        log_write(f"❌ FAILED: {step_name}")
        log_write(f"Error: {str(e)}")
        log_write(f"Traceback: {traceback.format_exc()}")
        return False

def test_basic_imports():
    """Test basic Python and package imports"""
    log_write(f"Python version: {sys.version}")
    log_write(f"Python executable: {sys.executable}")
    log_write(f"Current working directory: {os.getcwd()}")
    
    # Test basic imports
    import sqlalchemy
    log_write(f"SQLAlchemy version: {sqlalchemy.__version__}")
    
    import flask
    log_write(f"Flask version: {flask.__version__}")
    
    return "Basic imports successful"

def test_database_module():
    """Test database module import and initialization"""
    from src.database import init_database, DatabaseManager, Base
    log_write("Database module imported successfully")
    
    # Test database manager creation
    db_manager = DatabaseManager()
    log_write(f"DatabaseManager created: {type(db_manager)}")
    log_write(f"Default database URL: {db_manager.database_url}")
    
    return "Database module working"

def test_models_import():
    """Test importing all model classes"""
    from src.models import BaseModel, TimestampMixin, JSONMixin
    log_write("Base model classes imported")
    
    from src.models.user import User
    log_write("User model imported")
    
    from src.models.module import Module, Topic
    log_write("Module and Topic models imported")
    
    from src.models.exam import Exam, ExamSession
    log_write("Exam and ExamSession models imported")
    
    from src.models.question import Question, Answer
    log_write("Question and Answer models imported")
    
    from src.models.progress import UserProgress, UserResponse
    log_write("UserProgress and UserResponse models imported")
    
    return "All models imported successfully"

def test_database_connection():
    """Test database connection and table creation"""
    from src.database import init_database
    
    # Use in-memory SQLite for testing
    db_manager = init_database(database_url='sqlite:///:memory:', echo=True)
    log_write("Database manager initialized with in-memory SQLite")
    
    # Create tables
    db_manager.create_all_tables()
    log_write("Database tables created successfully")
    
    # Test session creation
    session = db_manager.get_session()
    log_write(f"Database session created: {type(session)}")
    session.close()
    
    return "Database connection and table creation successful"

def test_model_operations():
    """Test basic model operations"""
    from src.database import init_database
    from src.models.user import User
    from src.models.module import Module, Topic
    
    # Setup database
    db_manager = init_database(database_url='sqlite:///:memory:', echo=False)
    db_manager.create_all_tables()
    session = db_manager.get_session()
    
    try:
        # Test User creation
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpass')
        session.add(user)
        session.commit()
        log_write(f"User created: {user}")
        
        # Test Module creation
        module = Module(name='Test Module', description='Test module description')
        session.add(module)
        session.commit()
        log_write(f"Module created: {module}")
        
        # Test Topic creation
        topic = Topic(name='Test Topic', description='Test topic description', module=module)
        session.add(topic)
        session.commit()
        log_write(f"Topic created: {topic}")
        
        # Test queries
        users = session.query(User).all()
        log_write(f"Users in database: {len(users)}")
        
        modules = session.query(Module).all()
        log_write(f"Modules in database: {len(modules)}")
        
        return "Model operations successful"
        
    finally:
        session.close()

def test_flask_app():
    """Test Flask application creation"""
    from src.app import create_app
    
    app = create_app('testing')
    log_write(f"Flask app created: {app}")
    log_write(f"App config: {dict(app.config)}")
    
    # Test app context
    with app.app_context():
        log_write("Flask app context working")
        
        # Test database manager in app
        if hasattr(app, 'db_manager'):
            log_write(f"Database manager attached to app: {app.db_manager}")
        else:
            log_write("No database manager attached to app")
    
    return "Flask app creation successful"

def main():
    """Run all tests"""
    log_write(f"Starting SQLAlchemy Test Suite - {datetime.now().isoformat()}")
    log_write(f"Log file: {log_file}")
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Database Module", test_database_module),
        ("Models Import", test_models_import),
        ("Database Connection", test_database_connection),
        ("Model Operations", test_model_operations),
        ("Flask App", test_flask_app),
    ]
    
    results = []
    for test_name, test_func in tests:
        success = test_step(test_name, test_func)
        results.append((test_name, success))
    
    # Summary
    log_write(f"\n{'='*60}")
    log_write("TEST SUMMARY")
    log_write(f"{'='*60}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        log_write(f"{status}: {test_name}")
    
    log_write(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        log_write("🎉 ALL TESTS PASSED! SQLAlchemy implementation is working correctly.")
    else:
        log_write("⚠️  Some tests failed. Check the log for details.")
    
    log_write(f"\nTest completed at: {datetime.now().isoformat()}")
    log_write(f"Full log saved to: {log_file}")

if __name__ == "__main__":
    main()

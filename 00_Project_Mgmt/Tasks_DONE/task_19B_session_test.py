#!/usr/bin/env python3
"""
15-Minute Database Integration - Task 19B
Test SQLAlchemy session creation in app context
"""

print('=== TASK 19B: SQLAlchemy Session Test ===')

import sys
import os
sys.path.insert(0, 'src')

try:
    from src.app import create_app
    from src.database import DatabaseManager
    
    # Create Flask app
    app = create_app()
    print('✅ Flask app created successfully')
    
    # Test app context
    with app.app_context():
        print('✅ App context established')
        print(f'✅ Database URL: {app.config.get("SQLALCHEMY_DATABASE_URI")}')
        
        # Test database manager
        db_manager = app.db_manager
        print('✅ Database manager accessible')
        
        # Test session creation
        Session = db_manager.create_session_factory()
        session = Session()
        print('✅ SQLAlchemy session created')
        
        # Test basic query
        from sqlalchemy import text
        result = session.execute(text("SELECT count(*) FROM questions"))
        count = result.fetchone()[0]
        print(f'📊 Questions accessible via SQLAlchemy: {count}')
        
        session.close()
        print('✅ Session closed properly')

    print('✅ Task 19B COMPLETE: SQLAlchemy session working')
    
except ImportError as e:
    print(f'❌ Import error: {e}')
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()

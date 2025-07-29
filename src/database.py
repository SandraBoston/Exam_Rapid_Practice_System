"""
Database configuration and session management for PCEP Exam Accelerator.

This module provides SQLAlchemy database configuration, session management,
and database initialization functions.
"""

import os
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create the declarative base
Base = declarative_base()

class DatabaseManager:
    """Manages database connections and sessions."""
    
    def __init__(self, database_url=None, echo=False):
        """
        Initialize the database manager.
        
        Args:
            database_url (str): Database connection URL. If None, uses SQLite default.
            echo (bool): Whether to echo SQL statements to log.
        """
        if database_url is None:
            # Default to SQLite database in instance folder
            database_url = 'sqlite:///instance/pcep_exam.db'
        
        self.database_url = database_url
        self.echo = echo
        self.engine = None
        self.Session = None
        
    def create_engine(self):
        """Create and configure the SQLAlchemy engine."""
        if self.engine is not None:
            return self.engine
            
        # Special configuration for SQLite
        if self.database_url.startswith('sqlite'):
            self.engine = create_engine(
                self.database_url,
                echo=self.echo,
                poolclass=StaticPool,
                connect_args={
                    'check_same_thread': False,
                    'timeout': 30
                }
            )
            
            # Enable foreign key constraints for SQLite
            @event.listens_for(self.engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()
                
        else:
            self.engine = create_engine(
                self.database_url,
                echo=self.echo
            )
            
        logger.info(f"Database engine created for: {self.database_url}")
        return self.engine
    
    def create_session_factory(self):
        """Create a session factory."""
        if self.Session is not None:
            return self.Session
            
        engine = self.create_engine()
        self.Session = scoped_session(sessionmaker(
            bind=engine,
            autocommit=False,
            autoflush=False        ))
        
        logger.info("Database session factory created")
        return self.Session
    
    def database_exists(self):
        """Check if the database exists and is accessible."""
        try:
            engine = self.create_engine()
            
            # For SQLite, check if the file exists (unless it's in-memory)
            if self.database_url.startswith('sqlite:///'):
                if ':memory:' in self.database_url:
                    return True  # In-memory database always "exists"
                    
                db_path = self.database_url.replace('sqlite:///', '')
                if not os.path.exists(db_path):
                    return False
            
            # Try to connect and execute a simple query
            with engine.connect() as connection:
                # This will fail if database doesn't exist or is inaccessible
                from sqlalchemy import text
                connection.execute(text("SELECT 1"))
                return True
                
        except Exception as e:
            logger.debug(f"Database existence check failed: {e}")
            return False
    
    def get_session(self):
        """Get a database session."""
        Session = self.create_session_factory()
        return Session()
    
    def create_all_tables(self):
        """Create all database tables."""
        engine = self.create_engine()
        
        # Ensure instance directory exists (only for file-based SQLite)
        if self.database_url.startswith('sqlite:///') and not self.database_url.endswith(':memory:'):
            db_path = self.database_url.replace('sqlite:///', '')
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
        # Import all models to ensure they're registered
        from .models import user, module, exam, question, progress
        
        Base.metadata.create_all(engine)
        logger.info("All database tables created")
    
    def drop_all_tables(self):
        """Drop all database tables. Use with caution!"""
        engine = self.create_engine()
        Base.metadata.drop_all(engine)
        logger.warning("All database tables dropped")
    
    def close_connections(self):
        """Close all database connections."""
        if self.Session:
            self.Session.remove()
        if self.engine:
            self.engine.dispose()
        logger.info("Database connections closed")

# Global database manager instance
db_manager = None

def init_database(app=None, database_url=None, echo=False):
    """
    Initialize the database for a Flask application.
    
    Args:
        app: Flask application instance
        database_url (str): Database connection URL
        echo (bool): Whether to echo SQL statements
        
    Returns:
        DatabaseManager: Configured database manager
    """
    global db_manager
    
    if app is not None:
        # Get configuration from Flask app
        database_url = database_url or app.config.get('DATABASE_URL', 'sqlite:///instance/pcep_exam.db')
        echo = echo or app.config.get('SQLALCHEMY_ECHO', False)
    
    db_manager = DatabaseManager(database_url=database_url, echo=echo)
    
    if app is not None:
        # Store database manager in app for access in views
        app.db_manager = db_manager
        
        # Add teardown handler to close sessions
        @app.teardown_appcontext
        def close_db_session(error):
            if db_manager and db_manager.Session:
                db_manager.Session.remove()
    
    logger.info("Database initialized")
    return db_manager

def get_db_session():
    """Get a database session. For use in Flask request context."""
    if db_manager is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return db_manager.get_session()

def create_tables():
    """Create all database tables."""
    if db_manager is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    db_manager.create_all_tables()

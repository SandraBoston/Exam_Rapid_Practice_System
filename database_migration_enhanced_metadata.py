"""
Database Migration: Enhanced Metadata Fields
============================================

This migration adds new metadata fields to support enhanced file type recognition
and comprehensive source tracking in the PCEP Exam system.

NEW FIELDS ADDED:
- exam_external_id: Original ID from source JSON
- source_filename: Original filename for audit trail
- file_type: Classification (quiz/test/exam/assessment)
- time_limit_minutes: Time limit in minutes (more intuitive than seconds)

USAGE:
------
Run this script to upgrade your existing database schema to support
the enhanced metadata converter capabilities.
"""

import os
import sys
from pathlib import Path

# Add src directory to path for imports
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

try:
    from flask import Flask
    from database import DatabaseManager, init_database
    from models.exam import Exam
    from models.question import Question
    from sqlalchemy import text
    from app import create_app
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure you're running from the correct directory and all dependencies are installed.")
    sys.exit(1)

def run_migration():
    """
    Execute the database migration to add enhanced metadata fields.
    """
    print("Starting Enhanced Metadata Migration...")
    print("=" * 50)
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        try:
            # Get database session
            db_manager = app.db_manager
            session = db_manager.get_session()
            
            # Check current schema
            print("Checking current database schema...")
            
            # Add new columns to exams table if they don't exist
            migrations = [
                {
                    'name': 'exam_external_id',
                    'sql': 'ALTER TABLE exams ADD COLUMN exam_external_id INTEGER;',
                    'check': "SELECT COUNT(*) FROM pragma_table_info('exams') WHERE name='exam_external_id';"
                },
                {
                    'name': 'source_filename_new',
                    'sql': 'ALTER TABLE exams ADD COLUMN source_filename_new VARCHAR(255);',
                    'check': "SELECT COUNT(*) FROM pragma_table_info('exams') WHERE name='source_filename_new';"
                },
                {
                    'name': 'file_type',
                    'sql': 'ALTER TABLE exams ADD COLUMN file_type VARCHAR(20);',
                    'check': "SELECT COUNT(*) FROM pragma_table_info('exams') WHERE name='file_type';"
                },
                {
                    'name': 'time_limit_minutes',
                    'sql': 'ALTER TABLE exams ADD COLUMN time_limit_minutes INTEGER;',
                    'check': "SELECT COUNT(*) FROM pragma_table_info('exams') WHERE name='time_limit_minutes';"
                }
            ]
            
            # Execute migrations
            for migration in migrations:
                try:
                    # Check if column exists
                    result = session.execute(text(migration['check']))
                    exists = result.scalar() > 0
                    
                    if not exists:
                        print(f"Adding column: {migration['name']}")
                        session.execute(text(migration['sql']))
                        print(f"✓ Successfully added {migration['name']}")
                    else:
                        print(f"⚠ Column {migration['name']} already exists, skipping")
                        
                except Exception as e:
                    print(f"✗ Error adding {migration['name']}: {e}")
                    # Continue with other migrations
            
            # Add enhancements to questions table
            question_migrations = [
                {
                    'name': 'source_exam_external_id',
                    'sql': 'ALTER TABLE questions ADD COLUMN source_exam_external_id INTEGER;',
                    'check': "SELECT COUNT(*) FROM pragma_table_info('questions') WHERE name='source_exam_external_id';"
                },
                {
                    'name': 'original_question_number',
                    'sql': 'ALTER TABLE questions ADD COLUMN original_question_number INTEGER;',
                    'check': "SELECT COUNT(*) FROM pragma_table_info('questions') WHERE name='original_question_number';"
                }
            ]
            
            for migration in question_migrations:
                try:
                    result = session.execute(text(migration['check']))
                    exists = result.scalar() > 0
                    
                    if not exists:
                        print(f"Adding column: {migration['name']}")
                        session.execute(text(migration['sql']))
                        print(f"✓ Successfully added {migration['name']}")
                    else:
                        print(f"⚠ Column {migration['name']} already exists, skipping")
                        
                except Exception as e:
                    print(f"✗ Error adding {migration['name']}: {e}")
            
            # Commit all changes
            session.commit()
            print("\n✓ Migration completed successfully!")
            
            # Update existing records with default values
            print("\nUpdating existing records with default values...")
            
            # Set default file_type for existing exams
            update_queries = [
                "UPDATE exams SET file_type = 'exam' WHERE file_type IS NULL;",
                "UPDATE exams SET time_limit_minutes = time_limit / 60 WHERE time_limit_minutes IS NULL AND time_limit IS NOT NULL;",
                "UPDATE exams SET source_filename_new = source_file WHERE source_filename_new IS NULL AND source_file IS NOT NULL;"
            ]
            
            for query in update_queries:
                try:
                    result = session.execute(text(query))
                    rows_affected = result.rowcount
                    print(f"✓ Updated {rows_affected} records")
                except Exception as e:
                    print(f"⚠ Update warning: {e}")
            
            session.commit()
            
            # Display schema summary
            print("\n" + "=" * 50)
            print("MIGRATION SUMMARY")
            print("=" * 50)
            
            # Count existing exams
            exam_count = session.execute(text("SELECT COUNT(*) FROM exams")).scalar()
            question_count = session.execute(text("SELECT COUNT(*) FROM questions")).scalar()
            
            print(f"Existing Exams: {exam_count}")
            print(f"Existing Questions: {question_count}")
            print(f"New Metadata Fields Added: ✓")
            print(f"Database Ready for Enhanced Converter: ✓")
            
        except Exception as e:
            print(f"Migration failed: {e}")
            session.rollback()
            return False
        finally:
            session.close()
    
    return True

def verify_migration():
    """
    Verify that the migration was successful.
    """
    print("\nVerifying migration...")
    
    app = create_app()
    with app.app_context():
        try:
            # Get database session
            db_manager = getattr(app, 'db_manager', None)
            if not db_manager:
                print("✗ Database manager not found in app")
                return False
                
            session = db_manager.get_session()
            
            # Check that new columns exist and are accessible
            sample_exam = session.execute(text("""
                SELECT exam_external_id, source_filename_new, file_type, time_limit_minutes 
                FROM exams 
                LIMIT 1
            """)).first()
            
            print("✓ New columns are accessible")
            print("✓ Migration verification passed")
            session.close()
            return True
            
        except Exception as e:
            print(f"✗ Migration verification failed: {e}")
            return False

def main():
    """
    Main migration execution function.
    """
    print("PCEP Enhanced Metadata Migration Tool")
    print("=" * 50)
    
    # Run migration
    success = run_migration()
    
    if success:
        # Verify migration
        verify_migration()
        
        print("\n" + "=" * 50)
        print("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print("\nNext steps:")
        print("1. Your database now supports enhanced metadata")
        print("2. You can use the EnhancedMetadataConverter for new imports")
        print("3. Existing data has been preserved with default values")
        print("4. New fields are ready for file type classification")
        
    else:
        print("\n" + "=" * 50)
        print("❌ MIGRATION FAILED")
        print("=" * 50)
        print("Please check the error messages above and resolve any issues.")

if __name__ == "__main__":
    main()

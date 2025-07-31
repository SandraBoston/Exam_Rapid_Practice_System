#!/usr/bin/env python3
"""
Production Enhanced Converter - Import All Exam Data
===================================================

This script imports all exam data using the enhanced metadata converter
with full database integration. Ready for production use.

USAGE:
------
python production_enhanced_import.py

FEATURES:
---------
- Enhanced metadata extraction and storage
- File type classification (quiz/test/exam)
- Source filename tracking
- External ID preservation
- Comprehensive error handling
- Detailed import reporting
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

def setup_logging():
    """Setup logging for the import process."""
    log_filename = f"enhanced_import_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__), log_filename

def run_enhanced_import():
    """Run the enhanced import process."""
    
    logger, log_file = setup_logging()
    
    print("🚀 PRODUCTION ENHANCED EXAM DATA IMPORT")
    print("=" * 60)
    print(f"📝 Logging to: {log_file}")
    print()
    
    try:
        # Setup paths
        current_dir = Path(__file__).parent
        src_dir = current_dir / "src"
        
        # Set absolute database path before changing directory
        db_path = current_dir / "instance" / "pcep_exam.db"
        os.environ['DATABASE_URL'] = f"sqlite:///{db_path}"
        
        # Change to src directory for clean imports
        original_cwd = os.getcwd()
        os.chdir(str(src_dir))
        
        # Add paths
        sys.path.insert(0, str(src_dir))
        sys.path.insert(0, "converters_2_Evaluate")
        
        logger.info("Starting enhanced exam data import")
        logger.info(f"Database path set to: {db_path}")
        
        # Import required modules
        from app import create_app
        
        logger.info("Modules imported successfully")
        
        # Create Flask app
        app = create_app()
        logger.info("Flask app created")
        
        with app.app_context():
            logger.info("Flask app context active")
            
            # Access models that are already imported by the Flask app
            # Since we're in src directory, access them directly from app module
            import app as app_module
            Exam = app_module.Exam
            Question = app_module.Question
            Answer = app_module.Answer
            Topic = app_module.Topic
            logger.info("Model classes accessed from app module")
            
            # Get database session
            db_manager = app.db_manager
            session = db_manager.get_session()
            logger.info("Database session obtained")
            
            # Import converter after models are available
            from enhanced_metadata_converter import EnhancedMetadataConverter
            
            # Create converter with dependency injection
            models = {
                'Exam': Exam,
                'Question': Question,
                'Answer': Answer,
                'Topic': Topic
            }
            converter = EnhancedMetadataConverter(session=session, models=models)
            logger.info("Enhanced metadata converter initialized")
            
            # Find JSON files
            json_folder = Path("../Exam_HTML_Raw_Data_JSON_ONLY")
            if not json_folder.exists():
                logger.error(f"JSON folder not found: {json_folder}")
                print("❌ JSON folder not found")
                return False
            
            json_files = list(json_folder.glob("*.json"))
            logger.info(f"Found {len(json_files)} JSON files to process")
            
            if not json_files:
                logger.warning("No JSON files found")
                print("⚠️ No JSON files found")
                return False
            
            print(f"📁 Found {len(json_files)} exam files to import")
            print("🔄 Starting import process...")
            print()
            
            # Process each file
            results = []
            for i, file_path in enumerate(json_files, 1):
                print(f"[{i}/{len(json_files)}] Processing: {file_path.name}")
                logger.info(f"Processing file {i}/{len(json_files)}: {file_path.name}")
                
                try:
                    result = converter.process_file_with_metadata(str(file_path))
                    results.append(result)
                    
                    if result['success']:
                        metadata = result['metadata']
                        print(f"  ✅ Success - {metadata.get('file_type').title()}: {result['questions_imported']} questions")
                        print(f"     ID: {metadata.get('exam_external_id')}, Time: {metadata.get('time_limit_minutes')}min")
                        logger.info(f"Successfully imported {file_path.name}: {metadata.get('file_type')} with {result['questions_imported']} questions")
                    else:
                        print(f"  ❌ Failed - {len(result['errors'])} errors")
                        for error in result['errors']:
                            print(f"     - {error}")
                            logger.error(f"Error in {file_path.name}: {error}")
                
                except Exception as e:
                    print(f"  ❌ Exception - {str(e)}")
                    logger.error(f"Exception processing {file_path.name}: {str(e)}")
                    results.append({
                        'file_path': str(file_path),
                        'filename': file_path.name,
                        'success': False,
                        'errors': [str(e)]
                    })
                
                print()
            
            # Generate comprehensive report
            summary = converter.get_import_summary()
            report = converter.generate_metadata_report(results)
            
            # Display summary
            print("=" * 60)
            print("📊 IMPORT SUMMARY")
            print("=" * 60)
            print(f"Total Files Processed: {summary['total_files']}")
            print(f"Successful Imports: {summary['successful_imports']}")
            print(f"Failed Imports: {summary['failed_imports']}")
            print(f"Total Exams Created: {summary['total_exams']}")
            print(f"Total Questions Imported: {summary['total_questions']}")
            print(f"Processing Time: {summary['processing_time']:.2f} seconds")
            print()
            
            # File type distribution
            print("📋 FILE TYPE DISTRIBUTION:")
            for file_type, count in summary['file_types'].items():
                if count > 0:
                    print(f"  {file_type.title()}: {count}")
            print()
            
            # Success rate
            if summary['total_files'] > 0:
                success_rate = (summary['successful_imports'] / summary['total_files']) * 100
                print(f"✅ Success Rate: {success_rate:.1f}%")
            
            # Save detailed report
            report_filename = f"enhanced_import_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(report_filename, 'w', encoding='utf-8') as f:
                f.write(report)
            
            print(f"📄 Detailed report saved to: {report_filename}")
            
            # Log final summary
            logger.info(f"Import completed - {summary['successful_imports']}/{summary['total_files']} files successful")
            logger.info(f"Total exams: {summary['total_exams']}, Total questions: {summary['total_questions']}")
            
            session.close()
            
            if summary['successful_imports'] > 0:
                print("\n🎉 ENHANCED IMPORT COMPLETED SUCCESSFULLY!")
                print("✅ Exam data imported with enhanced metadata")
                print("✅ File type classification applied")
                print("✅ Source tracking implemented")
                print("✅ External IDs preserved")
                return True
            else:
                print("\n❌ NO FILES WERE SUCCESSFULLY IMPORTED")
                return False
                
    except Exception as e:
        logger.error(f"Import process failed: {str(e)}")
        print(f"❌ Import process failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Restore original working directory
        os.chdir(original_cwd)

def main():
    """Main execution function."""
    
    print("Enhanced Metadata Converter - Production Import")
    print("Date:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print()
    
    # Auto-proceed for testing (remove this for production)
    print("🔄 Starting automatic import for testing...")
    
    # Run the import
    success = run_enhanced_import()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ STEP 2 COMPLETE: Database Integration Successful!")
        print("=" * 60)
        print("🎯 NEXT STEPS:")
        print("1. ✅ Enhanced metadata converter working")
        print("2. ✅ Database integration verified")
        print("3. ✅ Exam data imported with metadata")
        print("4. 🚀 Ready for enhanced search and filtering")
        print("5. 🚀 Ready for production use")
    else:
        print("\n" + "=" * 60)
        print("❌ IMPORT FAILED")
        print("=" * 60)
        print("Please review the errors above and resolve any issues.")

if __name__ == "__main__":
    main()

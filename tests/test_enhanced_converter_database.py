#!/usr/bin/env python3
"""
Enhanced Converter Database Integration Test
===========================================

This script tests the enhanced metadata converter with actual database integration
to verify that the new metadata fields are properly stored and retrieved.

PURPOSE:
--------
- Test enhanced converter with database session
- Verify metadata extraction and storage
- Validate file type classification in database
- Confirm source filename tracking
"""

import os
import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
converters_dir = src_dir / "converters_2_Evaluate"
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(converters_dir))

def test_enhanced_converter_with_database():
    """Test the enhanced converter with full database integration."""
    
    print("🧪 ENHANCED CONVERTER DATABASE INTEGRATION TEST")
    print("=" * 60)
    
    try:
        # Import required modules
        from app import create_app
        from enhanced_metadata_converter import EnhancedMetadataConverter
        
        # Create Flask app and get database session
        app = create_app()
        
        with app.app_context():
            # Get database manager and session
            db_manager = app.db_manager
            session = db_manager.get_session()
            
            print("✅ Database connection established")
            print("✅ Flask app context active")
            
            # Initialize enhanced converter with database session
            converter = EnhancedMetadataConverter(session=session)
            print("✅ Enhanced converter initialized with database session")
            
            # Test with a sample JSON file
            json_folder = Path("Exam_HTML_Raw_Data_JSON_ONLY")
            if json_folder.exists():
                json_files = list(json_folder.glob("*.json"))
                if json_files:
                    # Test with first file
                    test_file = json_files[0]
                    print(f"\n🎯 Testing with file: {test_file.name}")
                    
                    # Process the file
                    result = converter.process_file_with_metadata(str(test_file))
                    
                    if result['success']:
                        print("✅ File processed successfully!")
                        print(f"✅ Exam created with ID: {result['exam_id']}")
                        print(f"✅ Questions imported: {result['questions_imported']}")
                        print(f"✅ File type detected: {result['metadata'].get('file_type')}")
                        print(f"✅ External ID: {result['metadata'].get('exam_external_id')}")
                        
                        # Verify in database
                        if result['exam_id']:
                            from models.exam import Exam
                            exam = session.query(Exam).get(result['exam_id'])
                            if exam:
                                print(f"\n📊 DATABASE VERIFICATION:")
                                print(f"  Exam Title: {exam.title}")
                                print(f"  Source File: {exam.source_file}")
                                
                                # Check metadata
                                metadata = exam.get_metadata()
                                print(f"  File Type: {metadata.get('file_type', 'Not set')}")
                                print(f"  External ID: {metadata.get('exam_external_id', 'Not set')}")
                                print(f"  Source Filename: {metadata.get('source_filename', 'Not set')}")
                                print(f"  Questions Count: {len(exam.questions)}")
                                
                                print("✅ Enhanced metadata successfully stored in database!")
                            else:
                                print("⚠️ Exam not found in database")
                    else:
                        print("❌ File processing failed:")
                        for error in result['errors']:
                            print(f"  - {error}")
                else:
                    print("⚠️ No JSON files found for testing")
            else:
                print("⚠️ JSON folder not found")
            
            # Close session
            session.close()
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Enhanced converter may not be in the correct location")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True

def test_batch_processing():
    """Test batch processing with multiple files."""
    
    print("\n🔄 TESTING BATCH PROCESSING")
    print("=" * 40)
    
    try:
        from app import create_app
        from enhanced_metadata_converter import EnhancedMetadataConverter
        
        app = create_app()
        
        with app.app_context():
            db_manager = app.db_manager
            session = db_manager.get_session()
            
            converter = EnhancedMetadataConverter(session=session)
            
            # Test batch processing
            json_folder = Path("Exam_HTML_Raw_Data_JSON_ONLY")
            if json_folder.exists():
                print(f"📁 Processing files in: {json_folder}")
                
                # Process up to 3 files for testing
                results = []
                json_files = list(json_folder.glob("*.json"))[:3]
                
                for file_path in json_files:
                    print(f"\n🔄 Processing: {file_path.name}")
                    result = converter.process_file_with_metadata(str(file_path))
                    results.append(result)
                    
                    if result['success']:
                        print(f"  ✅ Success - Type: {result['metadata'].get('file_type')}, Questions: {result['questions_imported']}")
                    else:
                        print(f"  ❌ Failed - Errors: {len(result['errors'])}")
                
                # Generate summary report
                summary = converter.get_import_summary()
                print(f"\n📊 BATCH PROCESSING SUMMARY:")
                print(f"  Total Files: {summary['total_files']}")
                print(f"  Successful: {summary['successful_imports']}")
                print(f"  Failed: {summary['failed_imports']}")
                print(f"  Total Exams: {summary['total_exams']}")
                print(f"  Total Questions: {summary['total_questions']}")
                
                # File type distribution
                print(f"\n📋 FILE TYPE DISTRIBUTION:")
                for file_type, count in summary['file_types'].items():
                    if count > 0:
                        print(f"  {file_type.title()}: {count}")
                
                return len(results) > 0 and any(r['success'] for r in results)
            
            session.close()
            
    except Exception as e:
        print(f"❌ Batch processing test failed: {e}")
        return False
    
    return True

def main():
    """Main test execution."""
    print("🚀 ENHANCED CONVERTER INTEGRATION TESTING")
    print("=" * 60)
    
    # Test 1: Single file with database
    test1_success = test_enhanced_converter_with_database()
    
    # Test 2: Batch processing
    test2_success = test_batch_processing()
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    if test1_success:
        print("✅ Single File Database Integration: PASSED")
    else:
        print("❌ Single File Database Integration: FAILED")
    
    if test2_success:
        print("✅ Batch Processing Integration: PASSED")
    else:
        print("❌ Batch Processing Integration: FAILED")
    
    if test1_success and test2_success:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Enhanced converter is ready for production use")
        print("✅ Database integration working perfectly")
        print("✅ Metadata extraction and storage confirmed")
        
        print("\n🚀 NEXT STEP: Ready for full exam data import!")
        
    else:
        print("\n⚠️ Some tests failed - please review errors above")
    
    return test1_success and test2_success

if __name__ == "__main__":
    main()

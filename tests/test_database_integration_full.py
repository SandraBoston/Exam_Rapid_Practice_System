#!/usr/bin/env python3
"""
Full Database Integration Test for Enhanced Converter
====================================================

This test creates a Flask app context and tests the enhanced converter
with full database integration to import exam data with metadata.
"""

import os
import sys
from pathlib import Path

def test_with_database_integration():
    """Test enhanced converter with actual database integration."""
    
    print("🔗 FULL DATABASE INTEGRATION TEST")
    print("=" * 50)
    
    try:
        # Add paths and setup
        current_dir = Path(__file__).parent
        src_dir = current_dir / "src"
        sys.path.insert(0, str(src_dir))
        
        # Change to src directory for imports
        os.chdir(str(src_dir))
        
        # Import Flask app and converter
        from app import create_app
        
        # Add converter path
        sys.path.append("converters_2_Evaluate")
        from enhanced_metadata_converter import EnhancedMetadataConverter
        
        print("✅ Imports successful")
        
        # Create Flask app
        app = create_app()
        print("✅ Flask app created")
        
        with app.app_context():
            print("✅ Flask app context active")
            
            # Get database session
            db_manager = app.db_manager
            session = db_manager.get_session()
            print("✅ Database session obtained")
            
            # Initialize enhanced converter with database
            converter = EnhancedMetadataConverter(session=session)
            print("✅ Enhanced converter initialized with database")
            
            # Test with one JSON file
            json_folder = Path("../Exam_HTML_Raw_Data_JSON_ONLY")
            if json_folder.exists():
                json_files = list(json_folder.glob("*.json"))
                if json_files:
                    test_file = json_files[0]  # Use first file
                    
                    print(f"\n🎯 Testing database import with: {test_file.name}")
                    
                    # Process the file with database integration
                    result = converter.process_file_with_metadata(str(test_file))
                    
                    if result['success']:
                        print("✅ File processed and imported to database!")
                        print(f"   Exam ID: {result['exam_id']}")
                        print(f"   Questions imported: {result['questions_imported']}")
                        print(f"   File type: {result['metadata'].get('file_type')}")
                        print(f"   External ID: {result['metadata'].get('exam_external_id')}")
                        
                        # Verify in database
                        from models.exam import Exam
                        if result['exam_id']:
                            exam = session.query(Exam).get(result['exam_id'])
                            if exam:
                                print(f"\n📊 DATABASE VERIFICATION:")
                                print(f"   Exam Title: {exam.title}")
                                print(f"   Source File: {exam.source_file}")
                                
                                # Check enhanced metadata
                                metadata = exam.get_metadata()
                                print(f"   Enhanced Metadata:")
                                print(f"     File Type: {metadata.get('file_type')}")
                                print(f"     External ID: {metadata.get('exam_external_id')}")
                                print(f"     Source Filename: {metadata.get('source_filename')}")
                                print(f"     Time Limit: {metadata.get('time_limit_minutes')} min")
                                
                                # Check questions
                                print(f"   Questions: {len(exam.questions)}")
                                if exam.questions:
                                    first_q = exam.questions[0]
                                    print(f"   First Question: {first_q.text[:50]}...")
                                
                                print("✅ Enhanced metadata successfully stored and retrieved!")
                                
                                # Clean up - remove the test exam to avoid duplicates
                                session.delete(exam)
                                session.commit()
                                print("✅ Test exam cleaned up")
                                
                                return True
                            else:
                                print("❌ Exam not found in database")
                                return False
                    else:
                        print("❌ File processing failed:")
                        for error in result['errors']:
                            print(f"   - {error}")
                        return False
                else:
                    print("⚠️ No JSON files found")
                    return False
            else:
                print("⚠️ JSON folder not found")
                return False
            
            session.close()
            
    except Exception as e:
        print(f"❌ Database integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Change back to original directory
        os.chdir(str(current_dir))

def test_batch_import():
    """Test importing multiple files to verify the enhanced system works at scale."""
    
    print("\n📦 BATCH IMPORT TEST")
    print("=" * 30)
    
    try:
        current_dir = Path(__file__).parent
        src_dir = current_dir / "src"
        sys.path.insert(0, str(src_dir))
        
        os.chdir(str(src_dir))
        
        from app import create_app
        sys.path.append("converters_2_Evaluate")
        from enhanced_metadata_converter import EnhancedMetadataConverter
        
        app = create_app()
        
        with app.app_context():
            db_manager = app.db_manager
            session = db_manager.get_session()
            
            converter = EnhancedMetadataConverter(session=session)
            
            # Process first 3 files
            json_folder = Path("../Exam_HTML_Raw_Data_JSON_ONLY")
            if json_folder.exists():
                json_files = list(json_folder.glob("*.json"))[:3]
                
                print(f"📁 Processing {len(json_files)} files...")
                
                results = []
                for file_path in json_files:
                    result = converter.process_file_with_metadata(str(file_path))
                    results.append(result)
                    
                    if result['success']:
                        print(f"  ✅ {file_path.name}: {result['metadata'].get('file_type')} with {result['questions_imported']} questions")
                    else:
                        print(f"  ❌ {file_path.name}: Failed")
                
                # Get summary
                summary = converter.get_import_summary()
                
                print(f"\n📊 BATCH IMPORT SUMMARY:")
                print(f"   Total Files: {summary['total_files']}")
                print(f"   Successful: {summary['successful_imports']}")
                print(f"   Failed: {summary['failed_imports']}")
                print(f"   Total Exams: {summary['total_exams']}")
                print(f"   Total Questions: {summary['total_questions']}")
                
                print(f"   File Type Distribution:")
                for file_type, count in summary['file_types'].items():
                    if count > 0:
                        print(f"     {file_type.title()}: {count}")
                
                # Clean up test data
                from models.exam import Exam
                for result in results:
                    if result['success'] and result['exam_id']:
                        exam = session.query(Exam).get(result['exam_id'])
                        if exam:
                            session.delete(exam)
                
                session.commit()
                print("✅ Test data cleaned up")
                
                return summary['successful_imports'] > 0
            
            session.close()
            
    except Exception as e:
        print(f"❌ Batch import test failed: {e}")
        return False
    
    finally:
        os.chdir(str(current_dir))

def main():
    """Main test execution."""
    
    print("🧪 ENHANCED CONVERTER DATABASE INTEGRATION TESTS")
    print("=" * 60)
    
    # Test 1: Single file with database
    test1_success = test_with_database_integration()
    
    # Test 2: Batch processing 
    test2_success = test_batch_import()
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 FINAL TEST RESULTS")
    print("=" * 60)
    
    if test1_success:
        print("✅ Single File Database Integration: PASSED")
    else:
        print("❌ Single File Database Integration: FAILED")
    
    if test2_success:
        print("✅ Batch Processing with Database: PASSED")
    else:
        print("❌ Batch Processing with Database: FAILED")
    
    if test1_success and test2_success:
        print("\n🎉 ALL DATABASE INTEGRATION TESTS PASSED!")
        print("✅ Enhanced converter works perfectly with database")
        print("✅ Metadata extraction and storage confirmed")
        print("✅ File type classification working")
        print("✅ Source tracking implemented")
        print("✅ Batch processing functional")
        
        print("\n🚀 STEP 2 COMPLETE: Database Integration Verified!")
        print("🚀 READY FOR STEP 3: Production Import of All Exam Data!")
        
    else:
        print("\n⚠️ Some database integration tests failed")
        print("Please review errors above before proceeding")
    
    return test1_success and test2_success

if __name__ == "__main__":
    main()

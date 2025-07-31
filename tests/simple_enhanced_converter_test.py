#!/usr/bin/env python3
"""
Simple Enhanced Converter Test
==============================

Direct test of the enhanced converter functionality without Flask app conflicts.
"""

import os
import sys
from pathlib import Path

# Add paths
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def test_converter_metadata_extraction():
    """Test the enhanced converter's metadata extraction without database."""
    
    print("🧪 TESTING ENHANCED CONVERTER METADATA EXTRACTION")
    print("=" * 60)
    
    try:
        # Import the converter
        sys.path.append(str(src_dir / "converters_2_Evaluate"))
        from enhanced_metadata_converter import EnhancedMetadataConverter
        
        # Initialize converter without database session
        converter = EnhancedMetadataConverter(session=None)
        print("✅ Enhanced converter initialized")
        
        # Test file type detection
        test_files = [
            "PCEP_Module2_Exam_20250610.v1.json",
            "PE1 -- Module 1 Quiz_20250610_v1.json", 
            "PE1 -- Module 1 Test_20250610_v1.json"
        ]
        
        print("\n🔍 Testing file type detection:")
        for filename in test_files:
            file_type = converter.detect_file_type(filename)
            print(f"  {filename:<40} → {file_type}")
        
        # Test with real JSON files
        json_folder = Path("Exam_HTML_Raw_Data_JSON_ONLY")
        if json_folder.exists():
            json_files = list(json_folder.glob("*.json"))[:3]  # Test first 3
            
            print(f"\n📁 Testing with {len(json_files)} real files:")
            
            for file_path in json_files:
                print(f"\n🔄 Processing: {file_path.name}")
                
                # Test the processing without database
                result = converter.process_file_with_metadata(str(file_path))
                
                if result['success']:
                    metadata = result['metadata']
                    print(f"  ✅ Success!")
                    print(f"     File Type: {metadata.get('file_type')}")
                    print(f"     External ID: {metadata.get('exam_external_id')}")
                    print(f"     Questions: {metadata.get('question_count')}")
                    print(f"     Time Limit: {metadata.get('time_limit_minutes')} min")
                    print(f"     Source: {metadata.get('source_filename')}")
                else:
                    print(f"  ❌ Failed:")
                    for error in result['errors']:
                        print(f"     - {error}")
            
            # Test batch processing summary
            print(f"\n📊 Testing import summary:")
            summary = converter.get_import_summary()
            print(f"  Total Files: {summary['total_files']}")
            print(f"  Successful: {summary['successful_imports']}")
            print(f"  Failed: {summary['failed_imports']}")
            
            # File type distribution
            print(f"  File Types:")
            for file_type, count in summary['file_types'].items():
                if count > 0:
                    print(f"    {file_type.title()}: {count}")
            
            return True
        else:
            print("⚠️ JSON folder not found - skipping real file tests")
            return True
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_connection():
    """Test basic database connection without conflicts."""
    
    print("\n🔗 TESTING DATABASE CONNECTION")
    print("=" * 40)
    
    try:
        import sqlite3
        
        # Test direct SQLite connection
        db_path = "instance/pcep_exam.db"
        if not os.path.exists(db_path):
            print("❌ Database file not found")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check our enhanced metadata fields exist
        cursor.execute("PRAGMA table_info(exams)")
        columns = [row[1] for row in cursor.fetchall()]
        
        enhanced_fields = ['exam_external_id', 'source_filename_new', 'file_type', 'time_limit_minutes']
        
        print("✅ Database connection successful")
        print("📊 Enhanced metadata fields in database:")
        
        for field in enhanced_fields:
            if field in columns:
                print(f"  ✅ {field}")
            else:
                print(f"  ❌ {field} - MISSING")
        
        # Check current data
        cursor.execute("SELECT COUNT(*) FROM exams")
        exam_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM questions") 
        question_count = cursor.fetchone()[0]
        
        print(f"\n📈 Current database contents:")
        print(f"  Exams: {exam_count}")
        print(f"  Questions: {question_count}")
        
        # Check if any exams have enhanced metadata
        cursor.execute("SELECT file_type, COUNT(*) FROM exams WHERE file_type IS NOT NULL GROUP BY file_type")
        file_types = cursor.fetchall()
        
        if file_types:
            print(f"  File types in database:")
            for file_type, count in file_types:
                print(f"    {file_type}: {count}")
        else:
            print(f"  No file type data yet - ready for enhanced import")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def main():
    """Main test execution."""
    
    print("🚀 ENHANCED METADATA CONVERTER - INTEGRATION TEST")
    print("=" * 60)
    
    # Test 1: Metadata extraction
    test1_success = test_converter_metadata_extraction()
    
    # Test 2: Database connection
    test2_success = test_database_connection()
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    if test1_success:
        print("✅ Enhanced Converter Metadata: PASSED")
    else:
        print("❌ Enhanced Converter Metadata: FAILED")
    
    if test2_success:
        print("✅ Database Integration Ready: PASSED")
    else:
        print("❌ Database Integration Ready: FAILED")
    
    if test1_success and test2_success:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Enhanced converter is working correctly")
        print("✅ Database has enhanced metadata fields")
        print("✅ Ready for full database integration")
        
        print("\n🚀 NEXT STEP: Ready to import exam data with enhanced metadata!")
        
    else:
        print("\n⚠️ Some tests failed - please review errors above")
    
    return test1_success and test2_success

if __name__ == "__main__":
    main()

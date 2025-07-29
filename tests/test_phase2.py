#!/usr/bin/env python3
"""
Phase 2 Test Script - Tests batch processing capabilities without database
"""

import os
import sys
from pathlib import Path

# Check conda environment first
def check_environment():
    conda_env = os.environ.get('CONDA_DEFAULT_ENV', 'base')
    print(f"Current conda environment: {conda_env}")
    
    if conda_env != 'pcep_env':
        print("❌ WARNING: Not in pcep_env conda environment!")
        print("Please run: conda activate pcep_env")
        return False
    else:
        print("✅ Correct conda environment active: pcep_env")
        return True

def test_file_discovery():
    """Test file discovery capabilities"""
    print("\n🔍 Testing File Discovery")
    print("=" * 50)
    
    # Add src to path
    sys.path.insert(0, 'src')
    
    try:
        from phase2_batch_processor import Phase2BatchProcessor
        
        processor = Phase2BatchProcessor()
        
        # Test directories
        test_dirs = ["Exam_HTML_Raw_Data", "Exam_Raw_Data_JSON", "nonexistent_dir"]
        
        discovered = processor.discover_exam_files(test_dirs)
        
        print(f"✅ File discovery test completed")
        print(f"Found {len(discovered)} files:")
        
        for file_path, file_type in discovered[:5]:  # Show first 5
            print(f"  - {Path(file_path).name} ({file_type})")
        
        if len(discovered) > 5:
            print(f"  ... and {len(discovered) - 5} more files")
            
        return True
        
    except Exception as e:
        print(f"❌ File discovery test failed: {e}")
        return False

def test_error_resilience():
    """Test error handling and resilience features"""
    print("\n🛡️ Testing Error Resilience")
    print("=" * 50)
    
    try:
        from phase2_batch_processor import Phase2BatchProcessor
        
        processor = Phase2BatchProcessor()
        
        # Test retry logic (without actual file processing)
        print(f"✅ Max retries setting: {processor.max_retries}")
        print(f"✅ Retry delay: {processor.retry_delay} seconds")
        print(f"✅ Continue on error: {processor.continue_on_error}")
        
        # Test progress tracking
        def mock_progress_callback(current, total, message):
            print(f"  Progress callback: {current}/{total} - {message}")
        
        processor.set_progress_callback(mock_progress_callback)
        processor.update_progress(3, 10, "Test progress update")
        
        print("✅ Error resilience features initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error resilience test failed: {e}")
        return False

def test_batch_stats():
    """Test batch statistics tracking"""
    print("\n📊 Testing Batch Statistics")
    print("=" * 50)
    
    try:
        from phase2_batch_processor import Phase2BatchProcessor
        
        processor = Phase2BatchProcessor()
        
        # Check initial stats
        stats = processor.batch_stats
        print(f"✅ Batch stats initialized:")
        for key, value in stats.items():
            print(f"  - {key}: {value}")
        
        # Test summary (without actual processing)
        processor.batch_stats['total_files_found'] = 10
        processor.batch_stats['successful_files'] = ['file1.html', 'file2.json']
        processor.batch_stats['failed_files'] = ['file3.html']
        
        print(f"\n✅ Mock batch statistics:")
        print(f"  - Files found: {processor.batch_stats['total_files_found']}")
        print(f"  - Successful: {len(processor.batch_stats['successful_files'])}")
        print(f"  - Failed: {len(processor.batch_stats['failed_files'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Batch statistics test failed: {e}")
        return False

def main():
    """Run Phase 2 tests"""
    print("🚀 Testing Phase 2: Batch Processing & Error Resilience")
    print("=" * 70)
    
    # Check environment first
    if not check_environment():
        print("\n⚠️  Environment check failed. Some tests may not work correctly.")
    
    # Run tests
    tests = [
        test_file_discovery,
        test_error_resilience, 
        test_batch_stats
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test_func.__name__} crashed: {e}")
            failed += 1
    
    print(f"\n🏁 Phase 2 Testing Complete!")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print("=" * 70)

if __name__ == "__main__":
    main()

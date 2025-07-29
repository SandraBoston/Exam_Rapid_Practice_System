#!/usr/bin/env python3
"""
Test conda package availability and create practical solution
"""

import sys
import subprocess
import os

def test_conda_availability():
    """Test different ways to access conda"""
    print("🔍 Testing Conda Accessibility")
    print("=" * 40)
    
    # Test 1: Check if conda package is importable
    try:
        import conda
        print("✅ conda package is importable")
        print(f"   conda version: {conda.__version__}")
        return True, "conda_package"
    except ImportError:
        print("❌ conda package not available in this environment")
    
    # Test 2: Check if conda CLI is accessible
    try:
        result = subprocess.run(['conda', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ conda CLI accessible: {result.stdout.strip()}")
            return True, "conda_cli"
        else:
            print("❌ conda CLI failed")
    except Exception as e:
        print(f"❌ conda CLI error: {e}")
    
    # Test 3: Check environment variables for conda paths
    conda_exe = os.environ.get('CONDA_EXE')
    if conda_exe and os.path.exists(conda_exe):
        print(f"✅ conda executable found: {conda_exe}")
        return True, "conda_exe"
    else:
        print("❌ conda executable not found in environment")
    
    return False, "none"

def get_practical_conda_solution():
    """Determine the best practical approach for conda operations"""
    available, method = test_conda_availability()
    
    if not available:
        return {
            'success': False,
            'recommendation': 'Install conda package or ensure conda is in PATH',
            'method': 'none'
        }
    
    if method == "conda_package":
        return {
            'success': True,
            'method': 'conda_package',
            'recommendation': 'Use conda Python API directly',
            'implementation': 'import conda; use conda.api functions'
        }
    
    elif method == "conda_cli":
        return {
            'success': True,
            'method': 'conda_cli',
            'recommendation': 'Use subprocess to call conda CLI',
            'implementation': 'subprocess.run([\'conda\', ...])'
        }
    
    elif method == "conda_exe":
        conda_exe = os.environ.get('CONDA_EXE')
        return {
            'success': True,
            'method': 'conda_exe',
            'recommendation': 'Use full path to conda executable',
            'implementation': f'subprocess.run([\'{conda_exe}\', ...])'
        }

if __name__ == "__main__":
    print("🐍 Conda Package Availability Test")
    print("=" * 50)
    
    solution = get_practical_conda_solution()
    
    print("\n🎯 RECOMMENDED SOLUTION:")
    print(f"   Method: {solution.get('method', 'unknown')}")
    print(f"   Recommendation: {solution.get('recommendation', 'unknown')}")
    
    if 'implementation' in solution:
        print(f"   Implementation: {solution['implementation']}")
    
    print(f"\n✅ Can proceed: {solution['success']}")

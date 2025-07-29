#!/usr/bin/env python3
"""
PCEP Package Availability Checker for conda-forge
Checks which packages are available on conda-forge vs pip-only
"""

import subprocess
import sys
from typing import Dict, List, Tuple

def check_conda_forge_availability(package_name: str) -> Tuple[bool, str]:
    """
    Check if a package is available on conda-forge
    Returns (is_available, version_info)
    """
    try:
        # Run conda search for the package on conda-forge
        result = subprocess.run(
            ['conda', 'search', '-c', 'conda-forge', package_name],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and result.stdout.strip():
            # Parse the output to get latest version
            lines = result.stdout.strip().split('\n')
            for line in reversed(lines):
                if package_name in line and 'conda-forge' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        return True, parts[1]  # Return version
            return True, "unknown_version"
        else:
            return False, "not_available"
            
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        return False, "check_failed"

def check_packages():
    """Check all PCEP project packages for conda-forge availability"""
    
    # All packages from our environment.yml
    packages_to_check = [
        # Core packages currently in conda section
        "flask",
        "jinja2", 
        "werkzeug",
        "sqlalchemy",
        "alembic",
        "beautifulsoup4",
        "lxml",
        "requests",
        "pytest",
        "pytest-cov",
        "pytest-mock",
        "black",
        "flake8",
        "isort", 
        "gunicorn",
        "wtforms",
        "itsdangerous",
        
        # Packages currently in pip section that we want to check
        "flask-sqlalchemy",
        "flask-migrate", 
        "flask-wtf",
        "flask-login",
        "restrictedpython"
    ]
    
    print("🔍 Checking conda-forge availability for PCEP packages...")
    print("=" * 60)
    
    conda_forge_available = []
    pip_only = []
    
    for package in packages_to_check:
        print(f"Checking {package}...", end=" ")
        is_available, info = check_conda_forge_availability(package)
        
        if is_available:
            print(f"✅ Available on conda-forge ({info})")
            conda_forge_available.append((package, info))
        else:
            print(f"❌ Not available on conda-forge ({info})")
            pip_only.append(package)
    
    print("\n" + "=" * 60)
    print("📋 SUMMARY:")
    print("=" * 60)
    
    print(f"\n✅ Available on conda-forge ({len(conda_forge_available)} packages):")
    for package, version in conda_forge_available:
        print(f"  - {package} (latest: {version})")
    
    print(f"\n❌ Pip-only packages ({len(pip_only)} packages):")
    for package in pip_only:
        print(f"  - {package}")
    
    print("\n" + "=" * 60)
    print("📝 UPDATED environment.yml STRUCTURE:")
    print("=" * 60)
    
    print("\ndependencies:")
    print("  - python=3.9")
    print("  - pip")
    print("  ")
    print("  # Packages available on conda-forge:")
    for package, _ in conda_forge_available:
        print(f"  - {package}")
    
    if pip_only:
        print("  ")
        print("  # Pip-only packages:")
        print("  - pip:")
        for package in pip_only:
            # Convert back to original casing for Flask extensions
            if package.startswith('flask-'):
                package = 'Flask-' + package[6:].title()
            elif package == 'restrictedpython':
                package = 'RestrictedPython'
            print(f"    - {package}")

if __name__ == "__main__":
    try:
        check_packages()
    except KeyboardInterrupt:
        print("\n\n⚠️  Check interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error during check: {e}")
        sys.exit(1)

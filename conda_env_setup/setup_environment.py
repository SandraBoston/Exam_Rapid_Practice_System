#!/usr/bin/env python3
"""
PCEP Environment Setup Script
Run this as Administrator to properly set up the conda environment
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    print(f"Command: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main setup function"""
    
    print("🚀 PCEP Certification Exam Accelerator - Environment Setup")
    print("=" * 60)
    
    # Check if running as administrator
    try:
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("⚠️  WARNING: Not running as Administrator!")
            print("   Some conda operations may fail due to permissions.")
            input("   Press Enter to continue anyway...")
    except:
        pass
    
    project_dir = Path(__file__).parent
    env_file = project_dir / "environment.yml"
    
    print(f"📁 Project Directory: {project_dir}")
    print(f"📄 Environment File: {env_file}")
    
    if not env_file.exists():
        print(f"❌ Environment file not found: {env_file}")
        return False
    
    # Step 1: Remove existing environment if it exists
    print("\n" + "=" * 60)
    run_command("conda env remove -n pcep_env -y", "Removing existing pcep_env (if exists)")
    
    # Step 2: Create environment from file
    print("\n" + "=" * 60)
    if not run_command(f"conda env create -f {env_file}", "Creating conda environment from environment.yml"):
        print("❌ Failed to create environment from YAML. Trying manual approach...")
          # Fallback: Create basic environment and install packages manually
        if run_command("conda create -n pcep_env python=3.9 pip -y", "Creating basic conda environment"):
            print("\n🔄 Installing packages manually...")
            
            # Install all conda packages in a single command for better dependency resolution
            conda_packages = [
                "flask", "jinja2", "werkzeug", "sqlalchemy", "alembic",
                "beautifulsoup4", "lxml", "requests", "pytest", "pytest-cov", 
                "black", "flake8", "isort", "gunicorn", "wtforms", "itsdangerous"
            ]
            
            # Single conda install command for all packages
            conda_cmd = f"conda install -n pcep_env -c conda-forge {' '.join(conda_packages)} -y"
            run_command(conda_cmd, "Installing all conda-forge packages in single command")
            
            # Install pip packages in a single command
            pip_packages = [
                "Flask-SQLAlchemy>=2.5.0", "Flask-Migrate>=3.1.0", "Flask-WTF>=1.0.0",
                "Flask-Login>=0.6.0", "pytest-mock>=3.6.0", "RestrictedPython>=5.2.0"
            ]
            
            pip_cmd = f"conda run -n pcep_env pip install {' '.join(pip_packages)}"
            run_command(pip_cmd, "Installing Flask extensions via pip in single command")
    
    # Step 3: Verify installation
    print("\n" + "=" * 60)
    print("🔍 Verifying installation...")
    
    verification_commands = [
        ("conda env list", "Listing conda environments"),
        ("conda list -n pcep_env", "Listing installed packages in pcep_env"),
        ("conda run -n pcep_env python --version", "Checking Python version"),
        ("conda run -n pcep_env python -c \"import flask; print(f'Flask: {flask.__version__}')\"", "Testing Flask import"),
        ("conda run -n pcep_env python -c \"import sqlalchemy; print(f'SQLAlchemy: {sqlalchemy.__version__}')\"", "Testing SQLAlchemy import")
    ]
    
    for cmd, desc in verification_commands:
        run_command(cmd, desc)
    
    print("\n" + "=" * 60)
    print("✅ Environment setup completed!")
    print("\nTo use the environment:")
    print("  conda activate pcep_env")
    print("\nTo deactivate:")
    print("  conda deactivate")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ Setup failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)

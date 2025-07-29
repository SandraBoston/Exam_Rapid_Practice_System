#!/usr/bin/env python3
"""
PCEP Environment Setup Script - Optimized Version
Run this as Administrator to properly set up the conda environment with single commands
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
    """Main setup function - optimized for single commands"""
    
    print("🚀 PCEP Certification Exam Accelerator - Optimized Environment Setup")
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
    
    # Step 1: Remove existing environment if it exists
    print("\n" + "=" * 60)
    run_command("conda env remove -n pcep_env -y", "Removing existing pcep_env (if exists)")
    
    # Step 2: Try to create environment from YAML first (most efficient)
    print("\n" + "=" * 60)
    if env_file.exists():
        if run_command(f"conda env create -f {env_file}", "Creating conda environment from environment.yml"):
            print("✅ Environment created successfully from YAML file!")
        else:
            print("❌ YAML creation failed. Trying optimized manual approach...")
            return create_environment_manually_optimized()
    else:
        print("📄 No environment.yml found. Using optimized manual approach...")
        return create_environment_manually_optimized()
    
    # Step 3: Verify installation
    return verify_installation()

def create_environment_manually_optimized():
    """Create environment using optimized single commands"""
    
    print("\n🔄 Creating environment with optimized single commands...")
    
    # All conda-forge packages in one command
    conda_packages = [
        "python=3.9", "pip",  # Include python and pip in the create command
        "flask", "jinja2", "werkzeug", "sqlalchemy", "alembic",
        "beautifulsoup4", "lxml", "requests", "pytest", "pytest-cov", 
        "black", "flake8", "isort", "gunicorn", "wtforms", "itsdangerous"
    ]
    
    # Single command to create environment and install all conda packages
    create_cmd = f"conda create -n pcep_env -c conda-forge {' '.join(conda_packages)} -y"
    
    if not run_command(create_cmd, "Creating environment and installing all conda-forge packages"):
        return False
    
    # Install all pip packages in a single command
    pip_packages = [
        "Flask-SQLAlchemy>=2.5.0", "Flask-Migrate>=3.1.0", "Flask-WTF>=1.0.0",
        "Flask-Login>=0.6.0", "pytest-mock>=3.6.0", "RestrictedPython>=5.2.0"
    ]
    
    pip_cmd = f"conda run -n pcep_env pip install {' '.join(pip_packages)}"
    if not run_command(pip_cmd, "Installing all Flask extensions via pip"):
        return False
    
    return verify_installation()

def verify_installation():
    """Verify the installation"""
    
    print("\n" + "=" * 60)
    print("🔍 Verifying installation...")
    
    verification_commands = [
        ("conda env list", "Listing conda environments"),
        ("conda list -n pcep_env", "Listing installed packages in pcep_env"),
        ("conda run -n pcep_env python --version", "Checking Python version"),
        ("conda run -n pcep_env python -c \"import flask; print(f'Flask: {flask.__version__}')\"", "Testing Flask import"),
        ("conda run -n pcep_env python -c \"import sqlalchemy; print(f'SQLAlchemy: {sqlalchemy.__version__}')\"", "Testing SQLAlchemy import"),
        ("conda run -n pcep_env python -c \"import flask_sqlalchemy; print('Flask-SQLAlchemy: OK')\"", "Testing Flask-SQLAlchemy import")
    ]
    
    success_count = 0
    for cmd, desc in verification_commands:
        if run_command(cmd, desc):
            success_count += 1
    
    print("\n" + "=" * 60)
    if success_count == len(verification_commands):
        print("✅ Environment setup completed successfully!")
        print(f"✅ All {success_count}/{len(verification_commands)} verification tests passed!")
    else:
        print(f"⚠️  Environment setup completed with issues.")
        print(f"⚠️  {success_count}/{len(verification_commands)} verification tests passed.")
    
    print("\nTo use the environment:")
    print("  conda activate pcep_env")
    print("\nTo deactivate:")
    print("  conda deactivate")
    print("\nTo see all installed packages:")
    print("  conda list -n pcep_env")
    
    return success_count == len(verification_commands)

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ Setup failed!")
            sys.exit(1)
        else:
            print("\n🎉 Setup completed successfully!")
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)

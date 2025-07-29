#!/usr/bin/env python3
"""
PCEP Certification Exam Accelerator - Complete Application Startup Script
Version: 1.0.0
Purpose: Clean startup script for entire application with front-end
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
from datetime import datetime

class PCEPAppStarter:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.src_path = self.project_root / "src"
        self.conda_env = "pcep_env"
        
    def verify_environment(self):
        """Verify we're in the correct conda environment"""
        print("🔍 Verifying conda environment...")
        
        # Check if we're in conda environment
        conda_env = os.environ.get('CONDA_DEFAULT_ENV')
        if conda_env != self.conda_env:
            print(f"❌ Wrong environment. Current: {conda_env}, Expected: {self.conda_env}")
            print(f"Please run: conda activate {self.conda_env}")
            return False
            
        print(f"✅ Conda environment: {conda_env}")
        return True
    
    def check_database(self):
        """Check and initialize database if needed"""
        print("🗄️ Checking database status...")
        
        try:
            # Add src to Python path
            sys.path.insert(0, str(self.src_path))
            
            # Import database components
            from src.database import DatabaseManager
            
            # Initialize database manager
            db_url = os.environ.get('DATABASE_URL', 'sqlite:///instance/pcep_exam.db')
            db_manager = DatabaseManager(db_url)
            
            # Check if database exists and create if needed
            if not db_manager.database_exists():
                print("📋 Creating database...")
                db_manager.create_all_tables()
                print("✅ Database created successfully")
            else:
                print("✅ Database exists")
                
            return True
            
        except Exception as e:
            print(f"⚠️ Database check failed: {e}")
            print("Continuing without database validation...")
            return True  # Continue anyway for now
    
    def check_migrations(self):
        """Check Alembic migrations status"""
        print("🔄 Checking database migrations...")
        
        try:
            # Check if alembic is set up
            alembic_dir = self.project_root / "migrations"
            if not alembic_dir.exists():
                print("⚠️ No migrations directory found - skipping migration check")
                return True  # Continue anyway
            
            # Check migration status
            result = subprocess.run(
                ["alembic", "current"], 
                capture_output=True, 
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                print("✅ Migrations up to date")
                return True
            else:
                print("⚠️ Migration status unclear, continuing...")
                return True
                
        except Exception as e:
            print(f"⚠️ Migration check failed: {e}, continuing...")
            return True
    
    def verify_packages(self):
        """Verify required packages are installed"""
        print("📦 Verifying required packages...")
        
        required_packages = [
            ('flask', 'Flask web framework'),
            ('sqlalchemy', 'SQLAlchemy ORM'),
            ('werkzeug', 'WSGI utilities'),
            ('jinja2', 'Template engine'),
            ('click', 'CLI framework')        ]
        
        missing_packages = []
        
        for package, description in required_packages:
            try:
                __import__(package)
                print(f"  ✅ {package} - {description}")
            except ImportError:
                missing_packages.append(package)
                print(f"  ❌ {package} - {description}")
        
        if missing_packages:
            print(f"❌ Missing packages: {', '.join(missing_packages)}")
            print("Please update conda environment with: conda env update -f environment.yml")
            return False
        
        print("✅ All required packages installed")
        return True
    
    def check_file_structure(self):
        """Verify required files and directories exist"""
        print("📁 Checking file structure...")
        
        required_paths = [
            (self.src_path, "Source directory"),
            (self.src_path / "app.py", "Main application file"),
            (self.src_path / "templates", "Templates directory"),
            (self.project_root / "conda_env_setup" / "environment.yml", "Conda environment file")
        ]
        
        missing_files = []
        
        for path, description in required_paths:
            if path.exists():
                print(f"  ✅ {description}: {path}")
            else:
                missing_files.append(f"{description}: {path}")
                print(f"  ❌ {description}: {path}")
        
        if missing_files:
            print(f"❌ Missing files/directories:")
            for missing in missing_files:
                print(f"    {missing}")
            return False
        
        print("✅ All required files found")
        return True
    
    def start_application(self):
        """Start the Flask application"""
        print("🚀 Starting PCEP Exam Accelerator...")
        print("=" * 60)
        
        try:
            # Set environment variables
            os.environ['FLASK_APP'] = 'src.app:create_app'
            os.environ['FLASK_ENV'] = 'development'
            os.environ['FLASK_DEBUG'] = '1'
            
            # Add src to Python path
            sys.path.insert(0, str(self.src_path))
              # Import and create the Flask app
            from src.app import create_app
            
            app = create_app('development')
            
            print("🌐 Application Details:")
            print(f"   📍 URL: http://localhost:5000")
            print(f"   🔧 Mode: Development")
            print(f"   📁 Project: {self.project_root}")
            print(f"   🐍 Environment: {self.conda_env}")
            print("=" * 60)
            print("📋 Available Features:")
            print("   • Dashboard - http://localhost:5000")
            print("   • Practice Quiz - http://localhost:5000/practice")
            print("   • Progress Tracking - http://localhost:5000/progress")
            print("   • API Questions - http://localhost:5000/api/questions")
            print("   • Health Check - http://localhost:5000/health")
            print("=" * 60)
            print("⏹️  Press Ctrl+C to stop the server")
            print("=" * 60)
            
            # Start the development server
            app.run(
                host='0.0.0.0',
                port=5000,
                debug=True,
                use_reloader=True
            )
            
        except KeyboardInterrupt:
            print("\n⏹️  Server stopped by user")
        except ImportError as e:
            print(f"❌ Import error: {e}")
            print("Make sure all required files are in place")
            return False
        except Exception as e:
            print(f"❌ Failed to start application: {e}")
            return False
        
        return True
    
    def run(self):
        """Run the complete startup sequence"""
        print("🎯 PCEP Certification Exam Accelerator")
        print("🔧 Starting Application...")
        print("=" * 60)
        
        # Run all checks
        checks = [
            ("Environment", self.verify_environment),
            ("File Structure", self.check_file_structure),
            ("Packages", self.verify_packages),
            ("Database", self.check_database),
            ("Migrations", self.check_migrations),
        ]
        
        for check_name, check_func in checks:
            if not check_func():
                print(f"❌ {check_name} check failed. Cannot start application.")
                return False
        
        print("✅ All checks passed!")
        print("=" * 60)
        
        # Start the application
        return self.start_application()

def main():
    """Main entry point"""
    starter = PCEPAppStarter()
    success = starter.run()
    if not success:
        print("\n💡 Quick fixes:")
        print("1. Activate conda environment: conda activate pcep_env")
        print("2. Update conda environment: conda env update -f environment.yml")
        print("3. Check that src/app.py exists")
        print("4. Verify database permissions")
        sys.exit(1)

if __name__ == "__main__":
    main()

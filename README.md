# File Organizer - PCEP Rapid Practice App

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Clean](https://img.shields.io/badge/code%20style-clean-brightgreen.svg)](https://github.com/psf/black)

A sophisticated, AI-aware project file organization system that automatically categorizes and organizes your project files while maintaining safety and providing rollback capabilities.

## 🚀 Features

### Core Functionality
- **Smart File Categorization**: Automatically categorizes files into 11 predefined categories
- **AI Development Support**: Special handling for AI/ML project files with 9 specialized subfolders
- **Safety First**: Critical file protection with dependency analysis
- **Backup & Restore**: Comprehensive backup system with rollback capabilities
- **Multiple Modes**: Preview, dry-run, and live organization modes
- **Progress Tracking**: Real-time progress bars and detailed reporting

### File Categories
1. **00_Project_Mgmt** - Project management files (TODO, plans, workflows)
2. **01_AI_Dev** - AI development files with 9 specialized subfolders
3. **02_Design_Docs** - Design and specification documents
4. **03_Source_Code** - Non-critical source code files
5. **04_Dev_Tools** - Development tools and utilities
6. **05_Data** - Data files (CSV, JSON, databases)
7. **06_Env_Config** - Environment and configuration files
8. **07_Logs_Reports** - Log files and reports
9. **08_Documentation** - User documentation and guides
10. **09_Reference** - Reference materials and resources
11. **99_Archive** - Archive and backup files

### AI Development Subfolders
- `01_prompt_engineering` - Prompt engineering files
- `02_specification_prompts` - Specification prompts
- `03_design_prompts` - Design and architecture prompts
- `04_code_generation_prompts` - Code generation prompts
- `05_testing_prompts` - Testing and validation prompts
- `06_documentation_prompts` - Documentation prompts
- `07_prompt_library` - Reusable prompt templates
- `08_ai_lessons_learned` - AI insights and lessons
- `09_copilot_transcripts` - Copilot conversation logs

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- Standard library modules (no external dependencies required)

### Quick Install
```bash
# Clone or download the file organizer package
cd your_project_directory

# The file_organizer package should be in your project root
# No additional installation required - uses only Python standard library
```

### Package Structure
```
file_organizer/
├── __init__.py          # Package initialization and API
├── main.py              # Main workflow orchestration
├── config.py            # Configuration and constants
├── models.py            # Data models and structures
├── file_scanner.py      # File discovery and scanning
├── file_categorizer.py  # File categorization logic
├── safety_manager.py    # Safety checks and protection
├── backup_manager.py    # Backup and restore operations
├── file_operations.py   # File moving and organization
└── user_interface.py    # User interaction and display
```

## 🎯 Quick Start

### Basic Usage
```python
# Import the main functions
from file_organizer import quick_organize, analyze_project

# Analyze your project (safe, read-only)
stats = analyze_project('/path/to/your/project')
print(f"Found {stats['total_files']} files in {len(stats['category_breakdown'])} categories")

# Preview organization (no changes made)
quick_organize('/path/to/your/project', mode='preview')

# Dry run (simulate organization)
quick_organize('/path/to/your/project', mode='dry_run')

# Live organization (with backup)
quick_organize('/path/to/your/project', mode='live', safety_level='normal')
```

### Interactive Mode
```python
from file_organizer import run_interactive_mode

# Run with full user interaction
exit_code = run_interactive_mode()
```

### Command Line Usage
```bash
# Interactive mode
python -m file_organizer.main

# Automated mode with specific path
python -m file_organizer.main --path "/path/to/project" --mode dry_run

# Show help
python -m file_organizer.main --help

# Show version
python -m file_organizer.main --version

# Backup management
python -m file_organizer.main --backups
```

## 🛡️ Safety Features

### Critical File Protection
The system automatically protects critical files from being moved:
- Main application files (`main.py`, `app.py`, `run.py`)
- Configuration files (`config.json`, `.env`, `settings.py`)
- Package files (`setup.py`, `pyproject.toml`, `requirements.txt`)
- Git files (`.gitignore`, `.gitmodules`)
- IDE files (`.vscode/`, `.idea/`)

### Safety Levels
- **Strict**: Maximum protection, extensive checks
- **Normal**: Balanced protection and functionality (default)
- **Relaxed**: Minimal protection, maximum flexibility

### Backup System
- Automatic backup creation before live operations
- Compressed ZIP archives with manifest files
- Integrity verification and rollback capabilities
- Backup cleanup and management

## 📊 Usage Examples

### Example 1: Project Analysis
```python
from file_organizer import analyze_project

# Analyze project structure
stats = analyze_project('/path/to/my/project')

print(f"Project Analysis Results:")
print(f"Total Files: {stats['total_files']}")
print(f"Total Size: {stats['total_size_mb']:.1f} MB")
print(f"Critical Files: {stats['critical_files_count']}")

print("\nCategory Breakdown:")
for category, count in stats['category_breakdown'].items():
    print(f"  {category}: {count} files")
```

### Example 2: Safe Organization
```python
from file_organizer import run_automated_mode
from pathlib import Path

# Organize with dry run first
result = run_automated_mode(
    project_path=Path('/path/to/project'),
    mode='dry_run',
    safety_level='normal'
)

if result == 0:
    print("Dry run successful! Ready for live organization.")
    
    # Now do live organization
    result = run_automated_mode(
        project_path=Path('/path/to/project'),
        mode='live',
        safety_level='normal'
    )
```

### Example 3: Custom Integration
```python
from file_organizer import (
    scan_project_files, categorize_file, 
    create_project_backup, organize_project_files
)
from pathlib import Path

project_path = Path('/path/to/project')

# Step 1: Scan files
all_files = scan_project_files(project_path)
print(f"Found {len(all_files)} files")

# Step 2: Categorize files
for file_info in all_files:
    category = categorize_file(file_info)
    if category:
        print(f"{file_info.name} -> {category}")

# Step 3: Create backup (for live operations)
backup_dir = project_path / ".file_organizer_backups"
backup_result = create_project_backup(project_path, backup_dir, all_files)

if backup_result.success:
    print(f"Backup created: {backup_result.backup_path}")
```

## 🔧 Configuration

### Environment Variables
```bash
# Optional: Set default safety level
export FILE_ORGANIZER_SAFETY_LEVEL=normal

# Optional: Set default backup directory
export FILE_ORGANIZER_BACKUP_DIR=.file_organizer_backups
```

### Custom Configuration
```python
from file_organizer import FOLDER_CATEGORIES, SAFETY_CONFIG

# View current configuration
print("Available categories:", list(FOLDER_CATEGORIES.keys()))
print("Safety settings:", SAFETY_CONFIG)
```

## 🧪 Testing

### Run Test Suite
```python
# Run comprehensive tests
from file_organizer import validate_package
result = validate_package()

# Run full test suite
python test_file_organizer.py
```

### Package Validation
```python
import file_organizer

# Validate package integrity
file_organizer.validate_package()

# Get package info
info = file_organizer.get_package_info()
print(f"File Organizer v{info['version']}")
```

## 📁 Project Structure After Organization

```
your_project/
├── 00_Project_Mgmt/           # Project management files
├── 01_AI_Dev/                 # AI development files
│   ├── 01_prompt_engineering/
│   ├── 02_specification_prompts/
│   ├── 03_design_prompts/
│   ├── 04_code_generation_prompts/
│   ├── 05_testing_prompts/
│   ├── 06_documentation_prompts/
│   ├── 07_prompt_library/
│   ├── 08_ai_lessons_learned/
│   └── 09_copilot_transcripts/
├── 02_Design_Docs/            # Design documents
├── 03_Source_Code/            # Non-critical source code
├── 04_Dev_Tools/              # Development tools
├── 05_Data/                   # Data files
├── 06_Env_Config/             # Configuration files
├── 07_Logs_Reports/           # Logs and reports
├── 08_Documentation/          # Documentation
├── 09_Reference/              # Reference materials
├── 99_Archive/                # Archive files
├── .file_organizer_backups/   # Backup directory
├── main.py                    # Protected files stay in root
├── config.json                # Protected files stay in root
└── ...                        # Other critical files
```

## 🔍 Troubleshooting

### Common Issues

1. **Permission Errors**
   ```bash
   # Ensure you have write permissions
   chmod +w /path/to/project
   ```

2. **Import Errors**
   ```python
   # Ensure file_organizer is in your Python path
   import sys
   sys.path.insert(0, '/path/to/file_organizer_parent')
   ```

3. **Backup Failures**
   - Check available disk space
   - Verify write permissions for backup directory
   - Ensure no files are locked by other processes

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

from file_organizer import run_interactive_mode
run_interactive_mode()  # Will show detailed debug information
```

## 🤝 Contributing

### Development Setup
```bash
# Clone the repository
git clone <repository_url>
cd file_organizer

# Run tests
python test_file_organizer.py

# Validate package
python -c "import file_organizer; file_organizer.validate_package()"
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints for all functions
- Include comprehensive docstrings
- Maintain modular architecture

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for the PCEP Rapid Practice App project
- Designed with AI development workflows in mind
- Emphasizes safety and maintainability

## 📞 Support

For issues, questions, or contributions:
1. Check the troubleshooting section above
2. Run the package validation: `file_organizer.validate_package()`
3. Review the user manual for detailed usage instructions

---

**Version:** 1.0.0  
**Python Requirements:** 3.8+  
**Dependencies:** None (uses only Python standard library)  
**Last Updated:** July 2025
The solution implements a Flask-based web interface that displays exam questions and answers extracted from HTML files containing practice exams. The system stores exam data in a local SQLite database for fast access and offline use, with a comprehensive schema designed to maintain data integrity. Users can select exams, practice specific topics, track their progress with visualizations, and use an embedded Python interpreter to test code in real-time. The MVP 1.0 will deliver core functionality, with multi-user features planned for later versions.

## Solution Design (high-level):

### System Development Process Plan:
1. **DEFINE**: Complete PRD (Product Requirements Document)
2. **DESIGN**: Create comprehensive Design Document
3. **DEVELOP**: Implement code according to prioritized requirements
4. **DEBUG**: Thoroughly test and debug all components
5. **DOCUMENT**: Create complete documentation for the system
6. **DELIVER**: Deploy final working system to GitHub

### Prioritized Requirements (MVP Approach):
1. Core exam data extraction and storage functionality
2. Basic web interface for practice exam sessions
3. Question navigation and session management
4. Performance tracking and basic reporting
5. Python code syntax highlighting and interpreter

### Future Enhancements (Post-MVP):
1. Advanced performance visualization
2. Multi-user functionality and leaderboards
3. AI-powered question analysis and recommendations
4. Mobile responsive interface optimizations
5. Offline mode enhancements

### Solution Code Description (low-level design):
The system will consist of the following components:

1. **Data Extraction Module**:
   - Extract JSON exam data from HTML files
   - Process and validate question and answer format
   - Store in SQLite database with proper schema

2. **Web Interface Module**:
   - Flask-based UI for exam practice
   - Session management functionality
   - Code syntax highlighting using Pygments

3. **Exam Session Module**:
   - Timer and progress tracking
   - Question navigation and bookmarking
   - Answer submission and scoring

4. **Reporting Module**:
   - Performance statistics calculation
   - Data visualization using Matplotlib/Plotly
   - Export functionality for reports

5. **Utility Modules**:
   - Logging system with timestamped files
   - Error handling with informative messages
   - Database migration tools using Alembic

### Development Considerations:
- Ensure data integrity with unique IDs for questions and answers
- Use AI to verify and identify correct answers
- Properly categorize questions by topic, module, and difficulty
- Implement robust error handling and logging
- Use version control with version IDs in filenames

## List of SDLC Documents
1. Product Requirements Document (PRD)
2. Design Document
3. Code Implementation Plan
4. Testing Plan
5. User Documentation
6. Technical Documentation
7. CHANGELOG
8. Delivery Plan

## Application Instructions:
The application will be delivered with comprehensive installation and usage instructions, including:

1. **Installation**:
   - Required Python packages
   - Database setup commands
   - Configuration options

2. **Usage**:
   - Uploading exam data
   - Starting practice sessions
   - Interpreting performance reports
   - Customizing the interface

3. **Development**:
   - Project structure overview
   - Adding new features
   - Testing procedures
   - Version control guidelines

All code will be fully documented with comments and docstrings, and a complete set of runlogs will be maintained to track system operations and errors.

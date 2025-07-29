# 2. System Architecture and Core Modules

## 2.1 Overall Architecture

The PCEP Certification Exam Accelerator follows a modern, modular, layered architecture with clear separation of concerns. The system is designed as a Flask-based web application with SQLite database backend, organized into distinct modules that handle specific functional areas.

### 2.1.1 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Presentation Layer                       │
├─────────────────────────────────────────────────────────────────┤
│                         Web Browser                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  HTML/CSS   │  │ JavaScript  │  │   Charts    │              │
│  │  Templates  │  │ Components  │  │ Visualiza.  │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
                                  ↕ HTTP/AJAX
┌─────────────────────────────────────────────────────────────────┐
│                       Application Layer                        │
├─────────────────────────────────────────────────────────────────┤
│                    Flask Web Application                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ Controllers │  │    Routes   │  │   Helpers   │              │
│  │    (Views)  │  │ (Blueprints)│  │  (Utilities)│              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ Form Handlers│  │ Auth/Session│  │Template     │              │
│  │ (WTForms)   │  │ Management  │  │Filters      │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
                                  ↕ Function Calls
┌─────────────────────────────────────────────────────────────────┐
│                        Business Logic Layer                    │
├─────────────────────────────────────────────────────────────────┤
│                       Core Module Services                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │Data Extract │  │Exam Session │  │  Reporting  │              │
│  │   Module    │  │   Module    │  │   Module    │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   Python    │  │  Utilities  │  │  Security   │              │
│  │ Interpreter │  │  & Logging  │  │  Services   │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
                                  ↕ ORM/SQL Queries
┌─────────────────────────────────────────────────────────────────┐
│                         Data Access Layer                      │
├─────────────────────────────────────────────────────────────────┤
│                    Database Module (SQLAlchemy)                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │    Models   │  │    Query    │  │ Migrations  │              │
│  │   (ORM)     │  │   Builder   │  │ (Alembic)   │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ Data Access │  │ Connection  │  │Transaction  │              │
│  │   Layer     │  │   Manager   │  │  Manager    │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
                                  ↕ SQL/File System
┌─────────────────────────────────────────────────────────────────┐
│                         Persistence Layer                      │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   SQLite    │  │ File System │  │  Log Files  │              │
│  │  Database   │  │(Static/Data)│  │ (Rotating)  │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

### 2.1.2 Component Design Principles

**Layered Architecture**: Clear separation between presentation, business logic, data access, and persistence layers.

**Modular Design**: Each module has specific responsibilities and well-defined interfaces.

**Loose Coupling**: Modules communicate through defined interfaces, minimizing dependencies.

**High Cohesion**: Related functionality is grouped within individual modules.

### 2.1.3 Module Interaction Patterns

The system uses several interaction patterns to maintain clean architecture:

- **Service Layer Pattern**: Business logic encapsulated in service classes
- **Repository Pattern**: Data access abstracted through repository interfaces
- **MVC Pattern**: Model-View-Controller separation for web interface
- **Dependency Injection**: Modules receive dependencies through initialization

## 2.2 Core Modules Detailed Design

### 2.2.1 Data Extraction Module

**Purpose**: Extract and process exam data from HTML files and convert to structured JSON format.

**Key Responsibilities**:
- Parse HTML files containing exam questions and answers
- Extract embedded JSON data from HTML script tags
- Process and validate JSON data structures
- Import and export exam data in various formats
- Maintain data integrity during extraction and conversion

**Core Components**:
- **HTML Parser**: Extracts JSON data from HTML files using pattern matching
- **JSON Processor**: Normalizes and validates exam data structures
- **Data Import/Export Service**: Handles file operations and data transformation
- **Validation Engine**: Ensures data quality and completeness

**Integration Points**:
- **Database Module**: Provides extracted data for storage
- **Web Interface Module**: Receives uploaded files for processing
- **Utility Module**: Uses logging and error handling services

### 2.2.2 Database Module

**Purpose**: Handle all data persistence, retrieval, and manipulation operations using SQLAlchemy ORM.

**Key Responsibilities**:
- Define and maintain database schema using SQLAlchemy models
- Provide data access layer for CRUD operations
- Manage database migrations and schema evolution
- Ensure data integrity and consistency
- Handle connection management and transaction control
- Support offline usage through local SQLite database

**Core Components**:
- **SQLAlchemy Models**: ORM definitions for all database entities
- **Data Access Layer**: Abstracted interface for database operations
- **Migration Manager**: Handles schema changes using Alembic
- **Query Builder**: Constructs optimized database queries
- **Transaction Manager**: Manages database transactions and rollbacks

**Integration Points**:
- **All Modules**: Central data repository for the entire system
- **Data Extraction Module**: Receives processed exam data
- **Exam Session Module**: Stores session and progress data
- **Reporting Module**: Provides data for analytics and reports

### 2.2.3 Web Interface Module

**Purpose**: Provide comprehensive user interface for interacting with the system through a responsive web interface.

**Key Responsibilities**:
- Present user-friendly interface for navigating the application
- Render exam questions and answers with proper formatting
- Handle user input and form submissions
- Manage navigation between different application views
- Display performance metrics and visualizations
- Provide responsive design for desktop and mobile devices
- Handle user authentication and session management

**Core Components**:
- **Flask Application**: Main web application framework
- **Jinja2 Templates**: Dynamic HTML generation with template inheritance
- **Static Assets**: CSS, JavaScript, and media file management
- **Route Controllers**: Handle HTTP requests and coordinate responses
- **Form Handlers**: Process user input using WTForms
- **Authentication System**: User login and session management

**Integration Points**:
- **Database Module**: Retrieves data for display and persists user interactions
- **Exam Session Module**: Coordinates session management and progress tracking
- **Reporting Module**: Integrates performance visualizations
- **Python Interpreter Module**: Embeds code execution functionality

### 2.2.4 Exam Session Module

**Purpose**: Manage individual exam practice sessions, including timing, progress tracking, and user interaction.

**Key Responsibilities**:
- Create and manage exam sessions with proper initialization
- Implement exam timing and countdown functionality
- Track user progress through questions and answers
- Handle question navigation (next, previous, jump to specific)
- Store user answers and calculate immediate feedback
- Manage session state persistence and recovery
- Implement session completion and results calculation

**Core Components**:
- **Session Manager**: Coordinates overall session lifecycle
- **Timer Service**: Handles exam timing and countdown alerts
- **Progress Tracker**: Monitors user advancement through questions
- **Question Navigator**: Manages question sequencing and user navigation
- **Answer Processor**: Handles user input validation and scoring
- **State Manager**: Persists session state for recovery

**Integration Points**:
- **Database Module**: Stores session data and user answers
- **Web Interface Module**: Provides user interface for session interaction
- **Reporting Module**: Supplies session data for performance analysis
- **Utility Module**: Uses logging for session activity tracking

### 2.2.5 Reporting Module

**Purpose**: Generate comprehensive performance reports and visualizations for user progress tracking.

**Key Responsibilities**:
- Calculate performance statistics and metrics
- Generate visual reports using charts and graphs
- Provide detailed analysis of user strengths and weaknesses
- Export reports in multiple formats (PDF, CSV, HTML)
- Track performance trends over time
- Generate topic-specific analysis reports
- Create comparative analysis against benchmarks

**Core Components**:
- **Statistics Calculator**: Computes performance metrics and trends
- **Chart Generator**: Creates visual representations using Chart.js
- **Report Builder**: Constructs comprehensive report documents
- **Export Service**: Handles multiple output formats
- **Analytics Engine**: Performs advanced data analysis
- **Template System**: Manages report layouts and formatting

**Integration Points**:
- **Database Module**: Retrieves session and performance data
- **Web Interface Module**: Displays reports and visualizations
- **Exam Session Module**: Receives real-time performance data
- **Utility Module**: Uses logging and configuration services

### 2.2.6 Python Interpreter Module

**Purpose**: Execute Python code examples and provide interactive coding practice within the exam environment.

**Key Responsibilities**:
- Execute Python code safely in a controlled environment
- Capture and format code execution output
- Handle code syntax errors and runtime exceptions
- Provide syntax highlighting for code display
- Support interactive code examples within questions
- Implement security measures for code execution
- Handle code timeouts and resource limitations

**Core Components**:
- **Code Executor**: Safely runs Python code in isolated environment
- **Sandbox Environment**: Security wrapper for code execution
- **Output Formatter**: Processes and displays execution results
- **Syntax Highlighter**: Provides code formatting for display
- **Security Manager**: Implements execution restrictions and timeouts
- **Resource Monitor**: Tracks execution time and memory usage

**Integration Points**:
- **Web Interface Module**: Integrates code execution into exam interface
- **Exam Session Module**: Supports interactive coding questions
- **Utility Module**: Uses error handling and logging services
- **Database Module**: May store code execution history (optional)

### 2.2.7 Utilities and Logging Module

**Purpose**: Provide common functionality and system-wide services including logging, error handling, and configuration management.

**Key Responsibilities**:
- Implement comprehensive logging across all system components
- Provide centralized error handling and exception management
- Manage application configuration and settings
- Handle file system operations and path management
- Provide utility functions for common operations
- Implement caching mechanisms for performance optimization
- Manage system monitoring and health checks

**Core Components**:
- **Logger**: Centralized logging system with multiple handlers
- **Error Handler**: Global exception handling and error reporting
- **Configuration Manager**: Application settings and environment management
- **File Manager**: File system operations and path utilities
- **Cache Manager**: In-memory caching for frequently accessed data
- **Monitor**: System health and performance monitoring

**Integration Points**:
- **All Modules**: Provides foundational services used system-wide
- **Web Interface Module**: Handles application errors and logging
- **Database Module**: Logs database operations and errors
- **Exam Session Module**: Tracks session activities and errors

## 2.3 Module Interaction Flow

### 2.3.1 Data Flow Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   HTML Files    │───▶│ Data Extraction │───▶│   Database      │
│  (Exam Data)    │    │    Module       │    │    Module       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                         ▲
                              ▼                         │
┌─────────────────┐    ┌─────────────────┐              │
│   JSON Files    │───▶│   Validation    │──────────────┘
│ (Processed)     │    │   & Storage     │
└─────────────────┘    └─────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Web Interface  │◄──▶│  Exam Session   │◄──▶│   Database      │
│    Module       │    │    Module       │    │    Module       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                       │                         ▲
         │                       ▼                         │
         │              ┌─────────────────┐                │
         └──────────────│   Reporting     │────────────────┘
                        │    Module       │
                        └─────────────────┘
```

### 2.3.2 Control Flow Patterns

**Request Processing Flow**:
1. Web Interface receives user request
2. Route controller validates and processes request
3. Business logic modules perform required operations
4. Database module handles data persistence/retrieval
5. Response is formatted and returned to user

**Session Management Flow**:
1. User initiates exam session through Web Interface
2. Exam Session Module creates new session instance
3. Database Module stores session initialization data
4. Questions are retrieved and presented through Web Interface
5. User answers are processed and stored continuously
6. Session completion triggers Reporting Module for analysis

**Error Handling Flow**:
1. Errors are caught at module level
2. Utilities Module processes and logs errors
3. Appropriate error responses are generated
4. User is presented with meaningful error messages
5. System state is preserved for recovery

This architecture ensures scalability, maintainability, and clear separation of concerns while providing a robust foundation for the PCEP Certification Exam Accelerator system.

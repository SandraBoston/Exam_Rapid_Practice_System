# PCEP Exam Accelerator - Database Schema Documentation

## Overview
This document provides the complete database schema for the PCEP Exam Accelerator system. The system uses SQLAlchemy ORM with Alembic for migrations and supports a comprehensive exam management and user progress tracking system.

## Architecture
- **ORM**: SQLAlchemy with declarative base
- **Migration Management**: Alembic
- **Database**: SQLite (for development), easily configurable for PostgreSQL/MySQL
- **Base Classes**: Common functionality through inheritance

## Core Base Classes

### BaseModel
All models inherit from `BaseModel` which provides:
- `id`: Primary key (Integer, auto-increment)
- `created_at`: Timestamp when record was created
- `updated_at`: Timestamp when record was last modified
- `to_dict()`: Converts model to dictionary
- `to_json()`: Converts model to JSON string

### JSONMixin
Provides JSON field manipulation:
- `get_json_field(field_name)`: Parse JSON from text field
- `set_json_field(field_name, data)`: Store dict as JSON in text field

## Database Schema

### 1. Users Table (`users`)
**Purpose**: User authentication and profile management

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK, Auto-increment | Primary key |
| username | String(80) | Unique, Not Null, Indexed | Unique username |
| email | String(120) | Unique, Not Null, Indexed | User email address |
| password_hash | String(255) | Not Null | Hashed password |
| last_login | DateTime | Nullable | Last login timestamp |
| is_active | Boolean | Not Null, Default: True | Account status |
| profile_data | Text | Nullable | JSON storage for profile info |
| created_at | DateTime | Not Null | Record creation time |
| updated_at | DateTime | Not Null | Last update time |

**Relationships**:
- `exam_sessions`: One-to-many with ExamSession
- `user_progress`: One-to-many with UserProgress

### 2. Modules Table (`modules`)
**Purpose**: Top-level organization of exam content

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK, Auto-increment | Primary key |
| name | String(100) | Unique, Not Null | Module name |
| description | Text | Nullable | Module description |
| display_order | Integer | Not Null, Default: 0, Indexed | Display order |
| created_at | DateTime | Not Null | Record creation time |
| updated_at | DateTime | Not Null | Last update time |

**Relationships**:
- `topics`: One-to-many with Topic

### 3. Topics Table (`topics`)
**Purpose**: Specific subject areas within modules

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK, Auto-increment | Primary key |
| name | String(100) | Not Null | Topic name |
| description | Text | Nullable | Topic description |
| module_id | Integer | FK(modules.id), Not Null, Indexed | Parent module |
| display_order | Integer | Not Null, Default: 0, Indexed | Display order |
| created_at | DateTime | Not Null | Record creation time |
| updated_at | DateTime | Not Null | Last update time |

**Relationships**:
- `module`: Many-to-one with Module
- `questions`: One-to-many with Question
- `user_progress`: One-to-many with UserProgress

### 4. Exams Table (`exams`)
**Purpose**: Complete exam definitions with metadata

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK, Auto-increment | Primary key |
| title | String(200) | Not Null, Indexed | Exam title |
| description | Text | Nullable | Exam description |
| time_limit | Integer | Not Null, Default: 3600 | Time limit in seconds |
| total_questions | Integer | Not Null, Default: 0 | Number of questions |
| source_file | String(255) | Nullable | Original source file path |
| version | String(20) | Not Null, Default: '1.0' | Exam version |
| is_active | Boolean | Not Null, Default: True, Indexed | Active status |
| exam_metadata | Text | Nullable | JSON storage for metadata |
| **Enhanced Fields** | | | **Added for file type recognition** |
| exam_external_id | Integer | Indexed | Original ID from source JSON |
| source_filename_new | String(255) | Nullable | Original filename for audit |
| file_type | String(20) | Nullable | Classification: quiz/test/exam/assessment |
| time_limit_minutes | Integer | Nullable | Time limit in minutes |
| created_at | DateTime | Not Null | Record creation time |
| updated_at | DateTime | Not Null | Last update time |

**Relationships**:
- `questions`: One-to-many with Question
- `exam_sessions`: One-to-many with ExamSession

### 5. Questions Table (`questions`)
**Purpose**: Individual exam questions with rich content

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK, Auto-increment | Primary key |
| original_id | String(50) | Indexed | Reference to source data |
| text | Text | Not Null | Question text |
| html_content | Text | Nullable | Rich HTML content |
| difficulty | Integer | Not Null, Default: 1, Indexed | Difficulty (1-5 scale) |
| topic_id | Integer | FK(topics.id), Indexed | Associated topic |
| exam_id | Integer | FK(exams.id), Not Null, Indexed | Parent exam |
| code_snippet | Text | Nullable | Code examples |
| explanation | Text | Nullable | Question explanation |
| question_order | Integer | Not Null, Default: 0, Indexed | Order in exam |
| metadata | Text | Default: '{}' | JSON metadata |
| **Enhanced Fields** | | | **Added for source tracking** |
| source_exam_external_id | Integer | Nullable | Links to original exam's external ID |
| original_question_number | Integer | Nullable | Original question number |
| created_at | DateTime | Not Null | Record creation time |
| updated_at | DateTime | Not Null | Last update time |

**Relationships**:
- `topic`: Many-to-one with Topic
- `exam`: Many-to-one with Exam
- `answers`: One-to-many with Answer
- `user_responses`: One-to-many with UserResponse

### 6. Answers Table (`answers`)
**Purpose**: Multiple choice answers for questions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK, Auto-increment | Primary key |
| original_id | String(50) | Indexed | Reference to source data |
| text | Text | Not Null | Answer text |
| html_content | Text | Nullable | Rich HTML content |
| is_correct | Boolean | Not Null, Indexed | Correct answer flag |
| explanation | Text | Nullable | Answer explanation |
| question_id | Integer | FK(questions.id), Not Null, Indexed | Parent question |
| answer_order | Integer | Not Null, Default: 0, Indexed | Display order |
| created_at | DateTime | Not Null | Record creation time |
| updated_at | DateTime | Not Null | Last update time |

**Relationships**:
- `question`: Many-to-one with Question
- `user_responses`: One-to-many with UserResponse

### 7. Exam Sessions Table (`exam_sessions`)
**Purpose**: User attempts at taking exams

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK, Auto-increment | Primary key |
| user_id | Integer | FK(users.id), Not Null, Indexed | User taking exam |
| exam_id | Integer | FK(exams.id), Not Null, Indexed | Exam being taken |
| start_time | DateTime | Not Null, Default: now, Indexed | Session start |
| end_time | DateTime | Nullable | Session end |
| is_completed | Boolean | Not Null, Default: False, Indexed | Completion status |
| score | Float | Not Null, Default: 0.0 | Percentage score |
| total_questions | Integer | Not Null, Default: 0 | Total questions |
| correct_answers | Integer | Not Null, Default: 0 | Correct answers |
| time_spent | Integer | Not Null, Default: 0 | Time in seconds |
| session_data | Text | Nullable | JSON session metadata |
| created_at | DateTime | Not Null | Record creation time |
| updated_at | DateTime | Not Null | Last update time |

**Relationships**:
- `user`: Many-to-one with User
- `exam`: Many-to-one with Exam
- `user_responses`: One-to-many with UserResponse

### 8. User Progress Table (`user_progress`)
**Purpose**: Track user proficiency across topics

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK, Auto-increment | Primary key |
| user_id | Integer | FK(users.id), Not Null, Indexed | User |
| topic_id | Integer | FK(topics.id), Not Null, Indexed | Topic |
| proficiency_level | Float | Not Null, Default: 0.0, Indexed | 0.0-1.0 scale |
| questions_attempted | Integer | Not Null, Default: 0 | Total attempts |
| questions_correct | Integer | Not Null, Default: 0 | Correct answers |
| average_time | Float | Not Null, Default: 0.0 | Avg time per question |
| last_practice_date | DateTime | Nullable | Last practice session |
| created_at | DateTime | Not Null | Record creation time |
| updated_at | DateTime | Not Null | Last update time |

**Relationships**:
- `user`: Many-to-one with User
- `topic`: Many-to-one with Topic

### 9. User Responses Table (`user_responses`)
**Purpose**: Individual question responses during exam sessions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK, Auto-increment | Primary key |
| user_id | Integer | FK(users.id), Not Null, Indexed | User |
| question_id | Integer | FK(questions.id), Not Null, Indexed | Question |
| answer_id | Integer | FK(answers.id), Indexed | Selected answer |
| exam_session_id | Integer | FK(exam_sessions.id), Not Null, Indexed | Session |
| is_correct | Boolean | Not Null, Indexed | Correct response flag |
| time_taken | Float | Not Null, Default: 0.0 | Time in seconds |
| response_text | Text | Nullable | Free text response |
| confidence_level | Integer | Default: 3 | User confidence (1-5) |
| created_at | DateTime | Not Null | Record creation time |
| updated_at | DateTime | Not Null | Last update time |

**Relationships**:
- `user`: Many-to-one with User
- `question`: Many-to-one with Question
- `answer`: Many-to-one with Answer
- `exam_session`: Many-to-one with ExamSession

## Key Features

### Enhanced Metadata Support
Recent enhancements added file type recognition and source tracking:
- **File Type Classification**: Automatically detects quiz/test/exam/assessment types
- **Source Tracking**: Preserves original filenames and external IDs for audit trails
- **Time Limit Flexibility**: Supports both seconds and minutes for different use cases

### JSON Storage
Several tables use JSON text fields for flexible metadata:
- `users.profile_data`: Extended profile information
- `exams.exam_metadata`: Exam-specific metadata
- `questions.metadata`: Question type, multi-select flags, etc.
- `exam_sessions.session_data`: Session-specific data

### Performance Optimizations
Strategic indexing on:
- Foreign keys for efficient joins
- Search fields (username, email, exam titles)
- Filter fields (difficulty, is_active, is_completed)
- Temporal fields (start_time, last_practice_date)

### Data Integrity
- Cascade deletes for hierarchical relationships
- Foreign key constraints enforced
- Non-null constraints on critical fields
- Unique constraints on business keys

## Migration Strategy

### Current Alembic Setup
- **Environment**: Configured in `migrations/env.py`
- **Current Revision**: `6b538fb010b4` (baseline with enhanced metadata)
- **Migration Scripts**: Located in `migrations/versions/`

### Future Migration Planning
The schema is designed for evolution:
1. **Modular Structure**: Easy to add new content types
2. **JSON Fields**: Flexible for new metadata without schema changes
3. **Versioning Support**: Built-in version tracking for exams
4. **Index Strategy**: Performance-conscious design for scaling

### Best Practices for Future Changes
1. **Always use Alembic**: Never modify tables directly
2. **Test Migrations**: Use development database for testing
3. **Backup Strategy**: Always backup before major migrations
4. **Gradual Rollout**: Use feature flags for schema-dependent features
5. **Monitor Performance**: Watch query performance after schema changes

## Usage Examples

### Query Patterns
```python
# Get user's exam sessions with scores
user_sessions = session.query(ExamSession).filter(
    ExamSession.user_id == user_id,
    ExamSession.is_completed == True
).order_by(ExamSession.start_time.desc()).all()

# Get questions by difficulty and topic
questions = session.query(Question).filter(
    Question.topic_id == topic_id,
    Question.difficulty == difficulty_level
).order_by(Question.question_order).all()

# Get user progress across all topics
progress = session.query(UserProgress).filter(
    UserProgress.user_id == user_id
).join(Topic).order_by(Topic.display_order).all()
```

### Enhanced Metadata Queries
```python
# Find exams by file type
quiz_exams = session.query(Exam).filter(
    Exam.file_type == 'quiz',
    Exam.is_active == True
).all()

# Get questions with source tracking
questions_with_source = session.query(Question).filter(
    Question.source_exam_external_id == external_id
).order_by(Question.original_question_number).all()
```

This schema provides a robust foundation for the PCEP exam system with built-in flexibility for future enhancements while maintaining data integrity and performance.

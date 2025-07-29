# 3. Database Design

## 3.1 Database Schema

The PCEP Certification Exam Accelerator uses SQLite with SQLAlchemy ORM for data persistence. The schema is designed to support all functional requirements while maintaining data integrity, query efficiency, and support for offline usage. The design accommodates complex exam structures, user session management, and performance tracking.

### 3.1.1 Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│      User       │       │      Module     │       │      Exam       │
│─────────────────│       │─────────────────│       │─────────────────│
│ id (PK)         │       │ id (PK)         │       │ id (PK)         │
│ username        │       │ name            │       │ title           │
│ email           │       │ description     │       │ description     │
│ created_at      │       └─────────────────┘       │ time_limit      │
│ last_login      │              │                  │ created_at      │
└─────────────────┘              │ 1:N              │ updated_at      │
         │                       ▼                  │ source_file     │
         │ 1:N            ┌─────────────────┐       │ version         │
         │                │     Topic       │       └─────────────────┘
         ▼                │─────────────────│              │
┌─────────────────┐       │ id (PK)         │              │ 1:N
│  ExamSession    │       │ name            │              ▼
│─────────────────│       │ description     │       ┌─────────────────┐
│ id (PK)         │       │ module_id (FK)  │       │    Question     │
│ user_id (FK)    │       └─────────────────┘       │─────────────────│
│ exam_id (FK)    │              │                  │ id (PK)         │
│ start_time      │              │ 1:N              │ original_id     │
│ end_time        │              ▼                  │ text            │
│ is_completed    │       ┌─────────────────┐       │ html_content    │
│ score           │       │   Questions     │◄──────│ difficulty      │
└─────────────────┘       │                 │       │ topic_id (FK)   │
         │                │   (same as      │       │ exam_id (FK)    │
         │ 1:N            │   right side)   │       │ code_snippet    │
         ▼                │                 │       └─────────────────┘
┌─────────────────┐       └─────────────────┘              │
│  UserResponse   │                                        │ 1:N
│─────────────────│                                        ▼
│ id (PK)         │                                 ┌─────────────────┐
│ session_id (FK) │                                 │     Answer      │
│ question_id (FK)│                                 │─────────────────│
│ answer_id (FK)  │                                 │ id (PK)         │
│ is_correct      │                                 │ original_id     │
│ time_taken      │                                 │ text            │
│ created_at      │                                 │ html_content    │
└─────────────────┘                                 │ is_correct      │
                                                    │ explanation     │
┌─────────────────┐                                 │ question_id(FK) │
│  UserProgress   │                                 └─────────────────┘
│─────────────────│
│ id (PK)         │
│ user_id (FK)    │
│ topic_id (FK)   │
│ proficiency_level│
│ questions_attempted│
│ questions_correct │
│ updated_at      │
└─────────────────┘
```

## 3.2 Table Definitions

### 3.2.1 Users Table

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    profile_data TEXT -- JSON for additional profile information
);

-- Indexes for performance
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);
```

### 3.2.2 Modules Table

```sql
CREATE TABLE modules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_modules_display_order ON modules(display_order);
```

### 3.2.3 Topics Table

```sql
CREATE TABLE topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    module_id INTEGER,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (module_id) REFERENCES modules (id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_topics_module_id ON topics(module_id);
CREATE INDEX idx_topics_display_order ON topics(display_order);
CREATE UNIQUE INDEX idx_topics_name_module ON topics(name, module_id);
```

### 3.2.4 Exams Table

```sql
CREATE TABLE exams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    time_limit INTEGER DEFAULT 3600, -- in seconds
    total_questions INTEGER DEFAULT 0,
    source_file TEXT,
    version TEXT DEFAULT '1.0',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    metadata TEXT -- JSON for additional exam metadata
);

-- Indexes
CREATE INDEX idx_exams_title ON exams(title);
CREATE INDEX idx_exams_created_at ON exams(created_at);
CREATE INDEX idx_exams_is_active ON exams(is_active);
```

### 3.2.5 Questions Table

```sql
CREATE TABLE questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_id TEXT, -- ID from source data for reference
    text TEXT NOT NULL,
    html_content TEXT, -- Rich HTML content
    difficulty INTEGER DEFAULT 1, -- 1-5 scale
    topic_id INTEGER,
    exam_id INTEGER,
    code_snippet TEXT,
    explanation TEXT,
    question_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (exam_id) REFERENCES exams (id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics (id) ON DELETE SET NULL
);

-- Indexes
CREATE INDEX idx_questions_exam_id ON questions(exam_id);
CREATE INDEX idx_questions_topic_id ON questions(topic_id);
CREATE INDEX idx_questions_difficulty ON questions(difficulty);
CREATE INDEX idx_questions_original_id ON questions(original_id);
CREATE INDEX idx_questions_order ON questions(question_order);
```

### 3.2.6 Answers Table

```sql
CREATE TABLE answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_id TEXT, -- ID from source data for reference
    text TEXT NOT NULL,
    html_content TEXT, -- Rich HTML content
    is_correct BOOLEAN NOT NULL,
    explanation TEXT,
    question_id INTEGER,
    answer_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (question_id) REFERENCES questions (id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_answers_question_id ON answers(question_id);
CREATE INDEX idx_answers_is_correct ON answers(is_correct);
CREATE INDEX idx_answers_original_id ON answers(original_id);
CREATE INDEX idx_answers_order ON answers(answer_order);
```

### 3.2.7 ExamSessions Table

```sql
CREATE TABLE exam_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    exam_id INTEGER,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    is_completed BOOLEAN DEFAULT 0,
    score REAL DEFAULT 0.0, -- Percentage score
    total_questions INTEGER DEFAULT 0,
    correct_answers INTEGER DEFAULT 0,
    time_spent INTEGER DEFAULT 0, -- Total time in seconds
    session_data TEXT, -- JSON for additional session metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (exam_id) REFERENCES exams (id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_exam_sessions_user_id ON exam_sessions(user_id);
CREATE INDEX idx_exam_sessions_exam_id ON exam_sessions(exam_id);
CREATE INDEX idx_exam_sessions_start_time ON exam_sessions(start_time);
CREATE INDEX idx_exam_sessions_is_completed ON exam_sessions(is_completed);
```

### 3.2.8 UserResponses Table (formerly UserAnswers)

```sql
CREATE TABLE user_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER,
    question_id INTEGER,
    answer_id INTEGER,
    is_correct BOOLEAN NOT NULL,
    is_bookmarked BOOLEAN DEFAULT 0,
    is_skipped BOOLEAN DEFAULT 0,
    time_taken REAL DEFAULT 0.0, -- Time in seconds
    response_data TEXT, -- JSON for additional response metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES exam_sessions (id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions (id) ON DELETE CASCADE,
    FOREIGN KEY (answer_id) REFERENCES answers (id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_user_responses_session_id ON user_responses(session_id);
CREATE INDEX idx_user_responses_question_id ON user_responses(question_id);
CREATE INDEX idx_user_responses_is_correct ON user_responses(is_correct);
CREATE INDEX idx_user_responses_is_bookmarked ON user_responses(is_bookmarked);
CREATE UNIQUE INDEX idx_user_responses_session_question ON user_responses(session_id, question_id);
```

### 3.2.9 UserProgress Table

```sql
CREATE TABLE user_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    topic_id INTEGER,
    proficiency_level REAL DEFAULT 0.0, -- 0.0 to 1.0 scale
    questions_attempted INTEGER DEFAULT 0,
    questions_correct INTEGER DEFAULT 0,
    average_time REAL DEFAULT 0.0, -- Average time per question
    last_practice_date TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics (id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_user_progress_user_id ON user_progress(user_id);
CREATE INDEX idx_user_progress_topic_id ON user_progress(topic_id);
CREATE INDEX idx_user_progress_proficiency ON user_progress(proficiency_level);
CREATE UNIQUE INDEX idx_user_progress_user_topic ON user_progress(user_id, topic_id);
```

## 3.3 SQLAlchemy Models

### 3.3.1 Base Configuration

```python
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import json

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert model instance to dictionary"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result
    
    def update_from_dict(self, data):
        """Update model instance from dictionary"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
```

### 3.3.2 Core Models

```python
class User(BaseModel):
    __tablename__ = 'users'
    
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)
    profile_data = Column(Text)  # JSON storage
    
    # Relationships
    sessions = relationship("ExamSession", back_populates="user", cascade="all, delete-orphan")
    progress = relationship("UserProgress", back_populates="user", cascade="all, delete-orphan")
    
    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)
    
    def get_profile_data(self):
        return json.loads(self.profile_data) if self.profile_data else {}
    
    def set_profile_data(self, data):
        self.profile_data = json.dumps(data)

class Module(BaseModel):
    __tablename__ = 'modules'
    
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    display_order = Column(Integer, default=0)
    
    # Relationships
    topics = relationship("Topic", back_populates="module", cascade="all, delete-orphan")

class Topic(BaseModel):
    __tablename__ = 'topics'
    
    name = Column(String(100), nullable=False)
    description = Column(Text)
    module_id = Column(Integer, ForeignKey('modules.id'))
    display_order = Column(Integer, default=0)
    
    # Relationships
    module = relationship("Module", back_populates="topics")
    questions = relationship("Question", back_populates="topic")
    user_progress = relationship("UserProgress", back_populates="topic")

class Exam(BaseModel):
    __tablename__ = 'exams'
    
    title = Column(String(200), nullable=False)
    description = Column(Text)
    time_limit = Column(Integer, default=3600)  # seconds
    total_questions = Column(Integer, default=0)
    source_file = Column(String(255))
    version = Column(String(20), default='1.0')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    metadata = Column(Text)  # JSON storage
    
    # Relationships
    questions = relationship("Question", back_populates="exam", cascade="all, delete-orphan")
    sessions = relationship("ExamSession", back_populates="exam")
    
    def get_metadata(self):
        return json.loads(self.metadata) if self.metadata else {}
    
    def set_metadata(self, data):
        self.metadata = json.dumps(data)

class Question(BaseModel):
    __tablename__ = 'questions'
    
    original_id = Column(String(50))  # Reference to source data
    text = Column(Text, nullable=False)
    html_content = Column(Text)
    difficulty = Column(Integer, default=1)  # 1-5 scale
    topic_id = Column(Integer, ForeignKey('topics.id'))
    exam_id = Column(Integer, ForeignKey('exams.id'))
    code_snippet = Column(Text)
    explanation = Column(Text)
    question_order = Column(Integer, default=0)
    
    # Relationships
    topic = relationship("Topic", back_populates="questions")
    exam = relationship("Exam", back_populates="questions")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")
    user_responses = relationship("UserResponse", back_populates="question")

class Answer(BaseModel):
    __tablename__ = 'answers'
    
    original_id = Column(String(50))  # Reference to source data
    text = Column(Text, nullable=False)
    html_content = Column(Text)
    is_correct = Column(Boolean, nullable=False)
    explanation = Column(Text)
    question_id = Column(Integer, ForeignKey('questions.id'))
    answer_order = Column(Integer, default=0)
    
    # Relationships
    question = relationship("Question", back_populates="answers")
    user_responses = relationship("UserResponse", back_populates="answer")

class ExamSession(BaseModel):
    __tablename__ = 'exam_sessions'
    
    user_id = Column(Integer, ForeignKey('users.id'))
    exam_id = Column(Integer, ForeignKey('exams.id'))
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    is_completed = Column(Boolean, default=False)
    score = Column(Float, default=0.0)  # Percentage
    total_questions = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    time_spent = Column(Integer, default=0)  # seconds
    session_data = Column(Text)  # JSON storage
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    exam = relationship("Exam", back_populates="sessions")
    responses = relationship("UserResponse", back_populates="session", cascade="all, delete-orphan")
    
    def get_session_data(self):
        return json.loads(self.session_data) if self.session_data else {}
    
    def set_session_data(self, data):
        self.session_data = json.dumps(data)
    
    def calculate_score(self):
        if self.total_questions > 0:
            self.score = (self.correct_answers / self.total_questions) * 100
        return self.score

class UserResponse(BaseModel):
    __tablename__ = 'user_responses'
    
    session_id = Column(Integer, ForeignKey('exam_sessions.id'))
    question_id = Column(Integer, ForeignKey('questions.id'))
    answer_id = Column(Integer, ForeignKey('answers.id'))
    is_correct = Column(Boolean, nullable=False)
    is_bookmarked = Column(Boolean, default=False)
    is_skipped = Column(Boolean, default=False)
    time_taken = Column(Float, default=0.0)  # seconds
    response_data = Column(Text)  # JSON storage
    
    # Relationships
    session = relationship("ExamSession", back_populates="responses")
    question = relationship("Question", back_populates="user_responses")
    answer = relationship("Answer", back_populates="user_responses")
    
    def get_response_data(self):
        return json.loads(self.response_data) if self.response_data else {}
    
    def set_response_data(self, data):
        self.response_data = json.dumps(data)

class UserProgress(BaseModel):
    __tablename__ = 'user_progress'
    
    user_id = Column(Integer, ForeignKey('users.id'))
    topic_id = Column(Integer, ForeignKey('topics.id'))
    proficiency_level = Column(Float, default=0.0)  # 0.0 to 1.0
    questions_attempted = Column(Integer, default=0)
    questions_correct = Column(Integer, default=0)
    average_time = Column(Float, default=0.0)
    last_practice_date = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="progress")
    topic = relationship("Topic", back_populates="user_progress")
    
    def calculate_proficiency(self):
        if self.questions_attempted > 0:
            accuracy = self.questions_correct / self.questions_attempted
            # Simple proficiency calculation - can be made more sophisticated
            self.proficiency_level = min(accuracy * 1.2, 1.0)  # Slight boost for accuracy
        return self.proficiency_level
```

## 3.4 Database Migration Strategy

### 3.4.1 Alembic Configuration

```python
# alembic/env.py configuration
from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

from app.models import Base  # Import all models

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )
        
        with context.begin_transaction():
            context.run_migrations()
```

### 3.4.2 Migration Management

```python
class DatabaseManager:
    def __init__(self, database_url=None):
        self.database_url = database_url or 'sqlite:///pcep_exam.db'
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def initialize_database(self):
        """Initialize database with all tables"""
        Base.metadata.create_all(bind=self.engine)
        return True
    
    def drop_all_tables(self):
        """Drop all tables (for testing/reset)"""
        Base.metadata.drop_all(bind=self.engine)
        return True
    
    def get_session(self):
        """Get database session"""
        return self.SessionLocal()
    
    def apply_migrations(self):
        """Apply pending migrations using Alembic"""
        from alembic.config import Config
        from alembic import command
        
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        return True
    
    def create_migration(self, message):
        """Create new migration"""
        from alembic.config import Config
        from alembic import command
        
        alembic_cfg = Config("alembic.ini")
        command.revision(alembic_cfg, message=message, autogenerate=True)
        return True
```

## 3.5 Data Access Layer

### 3.5.1 Repository Pattern Implementation

```python
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

class BaseRepository(ABC):
    def __init__(self, session):
        self.session = session
    
    @abstractmethod
    def create(self, **kwargs):
        pass
    
    @abstractmethod
    def get_by_id(self, id: int):
        pass
    
    @abstractmethod
    def get_all(self):
        pass
    
    @abstractmethod
    def update(self, id: int, **kwargs):
        pass
    
    @abstractmethod
    def delete(self, id: int):
        pass

class ExamRepository(BaseRepository):
    def create(self, **kwargs):
        exam = Exam(**kwargs)
        self.session.add(exam)
        self.session.commit()
        return exam
    
    def get_by_id(self, id: int):
        return self.session.query(Exam).filter(Exam.id == id).first()
    
    def get_all(self):
        return self.session.query(Exam).filter(Exam.is_active == True).all()
    
    def get_by_title(self, title: str):
        return self.session.query(Exam).filter(Exam.title == title).first()
    
    def update(self, id: int, **kwargs):
        exam = self.get_by_id(id)
        if exam:
            for key, value in kwargs.items():
                setattr(exam, key, value)
            exam.updated_at = datetime.utcnow()
            self.session.commit()
        return exam
    
    def delete(self, id: int):
        exam = self.get_by_id(id)
        if exam:
            exam.is_active = False  # Soft delete
            self.session.commit()
        return exam

class QuestionRepository(BaseRepository):
    def create(self, **kwargs):
        question = Question(**kwargs)
        self.session.add(question)
        self.session.commit()
        return question
    
    def get_by_id(self, id: int):
        return self.session.query(Question).filter(Question.id == id).first()
    
    def get_all(self):
        return self.session.query(Question).all()
    
    def get_by_exam_id(self, exam_id: int):
        return self.session.query(Question).filter(Question.exam_id == exam_id).all()
    
    def get_by_topic_id(self, topic_id: int):
        return self.session.query(Question).filter(Question.topic_id == topic_id).all()
    
    def get_by_difficulty(self, difficulty: int):
        return self.session.query(Question).filter(Question.difficulty == difficulty).all()
    
    def update(self, id: int, **kwargs):
        question = self.get_by_id(id)
        if question:
            for key, value in kwargs.items():
                setattr(question, key, value)
            self.session.commit()
        return question
    
    def delete(self, id: int):
        question = self.get_by_id(id)
        if question:
            self.session.delete(question)
            self.session.commit()
        return question

class UserSessionRepository(BaseRepository):
    def create(self, **kwargs):
        session = ExamSession(**kwargs)
        self.session.add(session)
        self.session.commit()
        return session
    
    def get_by_id(self, id: int):
        return self.session.query(ExamSession).filter(ExamSession.id == id).first()
    
    def get_all(self):
        return self.session.query(ExamSession).all()
    
    def get_by_user_id(self, user_id: int):
        return self.session.query(ExamSession).filter(ExamSession.user_id == user_id).all()
    
    def get_active_sessions(self, user_id: int):
        return self.session.query(ExamSession).filter(
            ExamSession.user_id == user_id,
            ExamSession.is_completed == False
        ).all()
    
    def update(self, id: int, **kwargs):
        session = self.get_by_id(id)
        if session:
            for key, value in kwargs.items():
                setattr(session, key, value)
            self.session.commit()
        return session
    
    def delete(self, id: int):
        session = self.get_by_id(id)
        if session:
            self.session.delete(session)
            self.session.commit()
        return session
```

### 3.5.2 Query Patterns

```python
class QueryBuilder:
    def __init__(self, session):
        self.session = session
    
    def get_user_performance_stats(self, user_id: int):
        """Get comprehensive performance statistics for a user"""
        return self.session.query(
            Topic.name,
            UserProgress.proficiency_level,
            UserProgress.questions_attempted,
            UserProgress.questions_correct,
            UserProgress.average_time
        ).join(UserProgress).filter(UserProgress.user_id == user_id).all()
    
    def get_exam_difficulty_distribution(self, exam_id: int):
        """Get question difficulty distribution for an exam"""
        return self.session.query(
            Question.difficulty,
            func.count(Question.id).label('count')
        ).filter(Question.exam_id == exam_id).group_by(Question.difficulty).all()
    
    def get_topic_performance_trends(self, user_id: int, days: int = 30):
        """Get performance trends over time for a user"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return self.session.query(
            func.date(UserResponse.created_at).label('date'),
            Topic.name,
            func.avg(UserResponse.is_correct.cast(Float)).label('accuracy'),
            func.count(UserResponse.id).label('attempts')
        ).join(Question).join(Topic).join(ExamSession).filter(
            ExamSession.user_id == user_id,
            UserResponse.created_at >= cutoff_date
        ).group_by(
            func.date(UserResponse.created_at),
            Topic.name
        ).order_by(func.date(UserResponse.created_at)).all()
```

### 3.5.3 Transaction Management

```python
from contextlib import contextmanager

@contextmanager
def database_transaction(session):
    """Context manager for database transactions"""
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

class DatabaseService:
    def __init__(self, database_manager):
        self.db_manager = database_manager
    
    def execute_transaction(self, operations):
        """Execute multiple operations in a single transaction"""
        with database_transaction(self.db_manager.get_session()) as session:
            results = []
            for operation in operations:
                result = operation(session)
                results.append(result)
            return results
    
    def bulk_insert_questions(self, exam_id: int, questions_data: List[Dict]):
        """Bulk insert questions for an exam"""
        def insert_operations(session):
            questions = []
            for q_data in questions_data:
                question = Question(exam_id=exam_id, **q_data)
                session.add(question)
                questions.append(question)
            session.flush()  # Get IDs without committing
            return questions
        
        return self.execute_transaction([insert_operations])[0]
```

This comprehensive database design provides a robust foundation for the PCEP Certification Exam Accelerator, supporting complex queries, performance tracking, and scalable data management while maintaining data integrity and supporting offline usage requirements.

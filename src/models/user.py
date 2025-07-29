"""
User model for PCEP Exam Accelerator.

Handles user authentication, profile data, and relationships with exam sessions.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from . import BaseModel, JSONMixin

class User(BaseModel, JSONMixin):
    """
    User model for authentication and profile management.
    """
    __tablename__ = 'users'
    
    # Basic user information
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Profile and status
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True, nullable=False)
    profile_data = Column(Text)  # JSON storage for additional profile information
    
    # Relationships
    exam_sessions = relationship("ExamSession", back_populates="user", cascade="all, delete-orphan")
    user_progress = relationship("UserProgress", back_populates="user", cascade="all, delete-orphan")
    
    def set_password(self, password):
        """
        Set user password with secure hashing.
        
        Args:
            password (str): Plain text password
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """
        Check if provided password matches stored hash.
        
        Args:
            password (str): Plain text password to verify
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return check_password_hash(str(self.password_hash), password)
    
    def get_profile_data(self):
        """
        Get user profile data as dictionary.
        
        Returns:
            dict: Profile data or empty dict if none
        """
        return self.get_json_field('profile_data')
    
    def set_profile_data(self, data):
        """
        Set user profile data from dictionary.
        
        Args:
            data (dict): Profile data to store
        """
        self.set_json_field('profile_data', data)
    
    def update_last_login(self):
        """Update the last login timestamp to current time."""
        self.last_login = datetime.utcnow()
    
    def is_authenticated(self):
        """Check if user is authenticated (active)."""
        return self.is_active
    
    def get_exam_history(self, limit=10):
        """
        Get user's recent exam sessions.
        
        Args:
            limit (int): Maximum number of sessions to return
            
        Returns:
            list: List of ExamSession objects
        """
        # Import here to avoid circular imports
        from .exam import ExamSession
        return (self.exam_sessions
                .filter_by(is_completed=True)
                .order_by(ExamSession.end_time.desc())
                .limit(limit)
                .all())
    
    def get_overall_progress(self):
        """
        Calculate overall progress across all topics.
        
        Returns:
            dict: Progress statistics
        """
        if not self.user_progress:
            return {
                'total_topics': 0,
                'completed_topics': 0,
                'average_proficiency': 0.0,
                'total_questions_attempted': 0,
                'total_questions_correct': 0,
                'overall_accuracy': 0.0
            }
        
        total_topics = len(self.user_progress)
        completed_topics = sum(1 for p in self.user_progress if p.proficiency_level >= 0.8)
        average_proficiency = sum(p.proficiency_level for p in self.user_progress) / total_topics
        total_questions_attempted = sum(p.questions_attempted for p in self.user_progress)
        total_questions_correct = sum(p.questions_correct for p in self.user_progress)
        overall_accuracy = (total_questions_correct / total_questions_attempted 
                          if total_questions_attempted > 0 else 0.0)
        
        return {
            'total_topics': total_topics,
            'completed_topics': completed_topics,
            'average_proficiency': round(average_proficiency, 3),
            'total_questions_attempted': total_questions_attempted,
            'total_questions_correct': total_questions_correct,
            'overall_accuracy': round(overall_accuracy, 3)
        }
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

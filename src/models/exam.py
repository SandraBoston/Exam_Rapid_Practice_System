"""
Exam and ExamSession models for PCEP Exam Accelerator.

Handles exam definitions and user exam sessions with scoring.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from . import BaseModel, JSONMixin

class Exam(BaseModel, JSONMixin):
    """
    Exam model representing a complete exam with questions and metadata.
    """
    __tablename__ = 'exams'
    
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    time_limit = Column(Integer, default=3600, nullable=False)  # seconds
    total_questions = Column(Integer, default=0, nullable=False)
    source_file = Column(String(255))  # Path to original source file
    version = Column(String(20), default='1.0', nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    exam_metadata = Column(Text)  # JSON storage for additional exam metadata (renamed to avoid SQLAlchemy conflict)
      # Relationships
    questions = relationship("Question", back_populates="exam", cascade="all, delete-orphan")
    exam_sessions = relationship("ExamSession", back_populates="exam")
    
    def get_metadata(self):
        """
        Get exam metadata as dictionary.
        
        Returns:
            dict: Metadata or empty dict if none
        """
        return self.get_json_field('exam_metadata')
    
    def set_metadata(self, data):
        """
        Set exam metadata from dictionary.
        
        Args:
            data (dict): Metadata to store
        """
        self.set_json_field('exam_metadata', data)
    
    def get_difficulty_distribution(self):
        """
        Get distribution of questions by difficulty level.
        
        Returns:
            dict: Difficulty levels as keys, counts as values
        """
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for question in self.questions:
            if question.difficulty in distribution:
                distribution[question.difficulty] += 1
        return distribution
    
    def get_topic_distribution(self):
        """
        Get distribution of questions by topic.
        
        Returns:
            dict: Topic names as keys, counts as values
        """
        distribution = {}
        for question in self.questions:
            if question.topic:
                topic_name = question.topic.name
                distribution[topic_name] = distribution.get(topic_name, 0) + 1
        return distribution
    
    def get_average_score(self):
        """
        Get average score across all completed sessions.
        
        Returns:
            float: Average score or 0.0 if no completed sessions
        """
        completed_sessions = [s for s in self.exam_sessions if s.is_completed]
        if not completed_sessions:
            return 0.0
        
        total_score = sum(s.score for s in completed_sessions)
        return round(total_score / len(completed_sessions), 2)
    
    def __repr__(self):
        return f"<Exam(id={self.id}, title='{self.title}', questions={len(self.questions)})>"

class ExamSession(BaseModel, JSONMixin):
    """
    ExamSession model representing a user's attempt at taking an exam.
    """
    __tablename__ = 'exam_sessions'
    
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    exam_id = Column(Integer, ForeignKey('exams.id'), nullable=False, index=True)
    start_time = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    end_time = Column(DateTime)
    is_completed = Column(Boolean, default=False, nullable=False, index=True)
    score = Column(Float, default=0.0, nullable=False)  # Percentage score
    total_questions = Column(Integer, default=0, nullable=False)
    correct_answers = Column(Integer, default=0, nullable=False)
    time_spent = Column(Integer, default=0, nullable=False)  # Total time in seconds
    session_data = Column(Text)  # JSON storage for additional session metadata
    
    # Relationships
    user = relationship("User", back_populates="exam_sessions")
    exam = relationship("Exam", back_populates="exam_sessions")
    user_responses = relationship("UserResponse", back_populates="exam_session", cascade="all, delete-orphan")
    
    def get_session_data(self):
        """
        Get session data as dictionary.
        
        Returns:
            dict: Session data or empty dict if none
        """
        return self.get_json_field('session_data')
    
    def set_session_data(self, data):
        """
        Set session data from dictionary.
        
        Args:
            data (dict): Session data to store
        """
        self.set_json_field('session_data', data)
    
    def calculate_score(self):
        """
        Calculate and update the session score based on user responses.
        
        Returns:
            float: Calculated score as percentage
        """
        if self.total_questions == 0:
            self.score = 0.0
            return self.score
        
        self.score = round((self.correct_answers / self.total_questions) * 100, 2)
        return self.score
    
    def complete_session(self):
        """Mark the session as completed and calculate final score."""
        self.end_time = datetime.utcnow()
        self.is_completed = True
        
        # Calculate time spent
        if self.start_time:
            self.time_spent = int((self.end_time - self.start_time).total_seconds())
        
        # Calculate final score
        self.calculate_score()
    
    def get_duration_minutes(self):
        """
        Get session duration in minutes.
        
        Returns:
            int: Duration in minutes, or 0 if not completed
        """
        if not self.end_time or not self.start_time:
            return 0
        
        duration = self.end_time - self.start_time
        return int(duration.total_seconds() / 60)
    
    def get_accuracy_percentage(self):
        """
        Get accuracy as percentage.
        
        Returns:
            float: Accuracy percentage
        """
        return self.score
    
    def get_responses_by_correctness(self, is_correct=True):
        """
        Get user responses filtered by correctness.
        
        Args:
            is_correct (bool): Whether to get correct or incorrect responses
            
        Returns:
            list: Filtered UserResponse objects
        """
        return [r for r in self.user_responses if r.is_correct == is_correct]
    
    def get_bookmarked_responses(self):
        """
        Get all bookmarked responses in this session.
        
        Returns:
            list: UserResponse objects that are bookmarked
        """
        return [r for r in self.user_responses if r.is_bookmarked]
    
    def __repr__(self):
        return f"<ExamSession(id={self.id}, user_id={self.user_id}, exam='{self.exam.title if self.exam else None}', score={self.score})>"

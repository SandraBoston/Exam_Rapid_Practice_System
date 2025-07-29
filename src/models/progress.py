"""
UserProgress and UserResponse models for PCEP Exam Accelerator.

Handles user progress tracking and individual question responses.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from . import BaseModel, JSONMixin

class UserProgress(BaseModel):
    """
    UserProgress model for tracking user proficiency across topics.
    """
    __tablename__ = 'user_progress'
    
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    topic_id = Column(Integer, ForeignKey('topics.id'), nullable=False, index=True)
    proficiency_level = Column(Float, default=0.0, nullable=False, index=True)  # 0.0 to 1.0 scale
    questions_attempted = Column(Integer, default=0, nullable=False)
    questions_correct = Column(Integer, default=0, nullable=False)
    average_time = Column(Float, default=0.0, nullable=False)  # Average time per question in seconds
    last_practice_date = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="user_progress")
    topic = relationship("Topic", back_populates="user_progress")
    
    def calculate_accuracy(self):
        """
        Calculate accuracy percentage.
        
        Returns:
            float: Accuracy as percentage (0.0 to 100.0)
        """
        if self.questions_attempted == 0:
            return 0.0
        return round((self.questions_correct / self.questions_attempted) * 100, 2)
    
    def update_progress(self, is_correct, time_taken):
        """
        Update progress with a new question attempt.
        
        Args:
            is_correct (bool): Whether the answer was correct
            time_taken (float): Time taken in seconds
        """
        # Update counters
        self.questions_attempted += 1
        if is_correct:
            self.questions_correct += 1
        
        # Update average time (running average)
        if self.average_time == 0:
            self.average_time = time_taken
        else:
            self.average_time = ((self.average_time * (self.questions_attempted - 1)) + time_taken) / self.questions_attempted
        
        # Update proficiency level (weighted by recent performance)
        accuracy = self.calculate_accuracy() / 100.0  # Convert to 0.0-1.0 scale
        
        # Weight recent performance more heavily
        if self.questions_attempted <= 5:
            # For first few questions, use straight accuracy
            self.proficiency_level = accuracy
        else:
            # Use weighted average favoring recent performance
            self.proficiency_level = (self.proficiency_level * 0.7) + (accuracy * 0.3)
        
        # Update last practice date
        self.last_practice_date = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def get_proficiency_label(self):
        """
        Get proficiency as a text label.
        
        Returns:
            str: Proficiency label
        """
        if self.proficiency_level >= 0.9:
            return "Expert"
        elif self.proficiency_level >= 0.8:
            return "Advanced"
        elif self.proficiency_level >= 0.7:
            return "Intermediate"
        elif self.proficiency_level >= 0.5:
            return "Beginner"
        else:
            return "Learning"
    
    def needs_practice(self, threshold=0.8):
        """
        Check if this topic needs more practice.
        
        Args:
            threshold (float): Proficiency threshold
            
        Returns:
            bool: True if proficiency is below threshold
        """
        return self.proficiency_level < threshold
    
    def __repr__(self):
        return f"<UserProgress(user_id={self.user_id}, topic='{self.topic.name if self.topic else None}', proficiency={self.proficiency_level:.2f})>"

class UserResponse(BaseModel, JSONMixin):
    """
    UserResponse model for tracking individual question responses in exam sessions.
    """
    __tablename__ = 'user_responses'
    
    exam_session_id = Column(Integer, ForeignKey('exam_sessions.id'), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False, index=True)
    answer_id = Column(Integer, ForeignKey('answers.id'), index=True)  # Nullable for skipped questions
    is_correct = Column(Boolean, nullable=False, index=True)
    is_bookmarked = Column(Boolean, default=False, nullable=False, index=True)
    is_skipped = Column(Boolean, default=False, nullable=False)
    time_taken = Column(Float, default=0.0, nullable=False)  # Time in seconds
    response_data = Column(Text)  # JSON storage for additional response metadata
    
    # Relationships
    exam_session = relationship("ExamSession", back_populates="user_responses")
    question = relationship("Question", back_populates="user_responses")
    answer = relationship("Answer", back_populates="user_responses")
    
    def get_response_data(self):
        """
        Get response data as dictionary.
        
        Returns:
            dict: Response data or empty dict if none
        """
        return self.get_json_field('response_data')
    
    def set_response_data(self, data):
        """
        Set response data from dictionary.
        
        Args:
            data (dict): Response data to store
        """
        self.set_json_field('response_data', data)
    
    def get_correctness_label(self):
        """
        Get correctness as a text label.
        
        Returns:
            str: "Correct", "Incorrect", or "Skipped"
        """
        if self.is_skipped:
            return "Skipped"
        return "Correct" if self.is_correct else "Incorrect"
    
    def get_time_label(self):
        """
        Get time taken as a formatted string.
        
        Returns:
            str: Time formatted as "MM:SS"
        """
        minutes = int(self.time_taken // 60)
        seconds = int(self.time_taken % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def is_fast_response(self, threshold=30.0):
        """
        Check if response was answered quickly.
        
        Args:
            threshold (float): Time threshold in seconds
            
        Returns:
            bool: True if answered faster than threshold
        """
        return self.time_taken < threshold and not self.is_skipped
    
    def is_slow_response(self, threshold=120.0):
        """
        Check if response took a long time.
        
        Args:
            threshold (float): Time threshold in seconds
            
        Returns:
            bool: True if took longer than threshold
        """
        return self.time_taken > threshold and not self.is_skipped
    
    def __repr__(self):
        return f"<UserResponse(session_id={self.exam_session_id}, question_id={self.question_id}, correct={self.is_correct})>"

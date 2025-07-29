"""
Module and Topic models for PCEP Exam Accelerator.

Handles the hierarchical organization of exam content by modules and topics.
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from . import BaseModel

class Module(BaseModel):
    """
    Module model for organizing exam content at the highest level.
    
    Modules contain topics and represent major areas of the PCEP curriculum.
    """
    __tablename__ = 'modules'
    
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    display_order = Column(Integer, default=0, nullable=False, index=True)
    
    # Relationships
    topics = relationship("Topic", back_populates="module", cascade="all, delete-orphan")
    
    def get_topic_count(self):
        """Get the number of topics in this module."""
        return len(self.topics)
    
    def get_question_count(self):
        """Get the total number of questions across all topics in this module."""
        return sum(topic.get_question_count() for topic in self.topics)
    
    def __repr__(self):
        return f"<Module(id={self.id}, name='{self.name}', topics={len(self.topics)})>"

class Topic(BaseModel):
    """
    Topic model for organizing exam content within modules.
    
    Topics are specific subject areas within modules and contain questions.
    """
    __tablename__ = 'topics'
    
    name = Column(String(100), nullable=False)
    description = Column(Text)
    module_id = Column(Integer, ForeignKey('modules.id'), nullable=False, index=True)
    display_order = Column(Integer, default=0, nullable=False, index=True)
    
    # Relationships
    module = relationship("Module", back_populates="topics")
    questions = relationship("Question", back_populates="topic")
    user_progress = relationship("UserProgress", back_populates="topic")
    
    def get_question_count(self):
        """Get the number of questions in this topic."""
        return len(self.questions)
    
    def get_average_difficulty(self):
        """
        Get the average difficulty of questions in this topic.
        
        Returns:
            float: Average difficulty (1-5 scale) or 0 if no questions
        """
        if not self.questions:
            return 0.0
        
        total_difficulty = sum(q.difficulty for q in self.questions)
        return round(total_difficulty / len(self.questions), 2)
    
    def get_questions_by_difficulty(self, difficulty):
        """
        Get questions filtered by difficulty level.
        
        Args:
            difficulty (int): Difficulty level (1-5)
            
        Returns:
            list: Questions with the specified difficulty
        """
        return [q for q in self.questions if q.difficulty == difficulty]
    
    def __repr__(self):
        return f"<Topic(id={self.id}, name='{self.name}', module='{self.module.name if self.module else None}', questions={len(self.questions)})>"

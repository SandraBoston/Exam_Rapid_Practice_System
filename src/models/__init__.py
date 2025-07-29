"""
Base model classes and database initialization for PCEP Exam Accelerator.

This module provides the base model classes and imports all model definitions
to ensure they are registered with SQLAlchemy.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, Text
import json

from database import Base

class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps to models."""
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class BaseModel(Base, TimestampMixin):
    """
    Base model class that provides common functionality for all models.
    """
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    def to_dict(self, include_relationships=False):
        """
        Convert model instance to dictionary.
        
        Args:
            include_relationships (bool): Whether to include relationship data
            
        Returns:
            dict: Dictionary representation of the model
        """
        result = {}
        
        # Add column data
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            else:
                result[column.name] = value
        
        # Add relationship data if requested
        if include_relationships:
            for relationship in self.__mapper__.relationships:
                value = getattr(self, relationship.key)
                if value is not None:
                    if hasattr(value, '__iter__') and not isinstance(value, (str, bytes)):
                        # Collection relationship
                        result[relationship.key] = [item.to_dict() if hasattr(item, 'to_dict') else str(item) for item in value]
                    else:
                        # Single relationship
                        result[relationship.key] = value.to_dict() if hasattr(value, 'to_dict') else str(value)
        
        return result
    
    def update_from_dict(self, data):
        """
        Update model instance from dictionary.
        
        Args:
            data (dict): Dictionary with field names and values
        """
        for key, value in data.items():
            if hasattr(self, key) and key not in ['id', 'created_at']:
                setattr(self, key, value)
        
        # Update the updated_at timestamp
        self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        """String representation of the model."""
        return f"<{self.__class__.__name__}(id={self.id})>"

class JSONMixin:
    """Mixin to add JSON field support to models."""
    
    def get_json_field(self, field_name):
        """
        Get JSON data from a text field.
        
        Args:
            field_name (str): Name of the field containing JSON data
            
        Returns:
            dict: Parsed JSON data or empty dict if None/invalid
        """
        field_value = getattr(self, field_name, None)
        if field_value:
            try:
                return json.loads(field_value)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
    
    def set_json_field(self, field_name, data):
        """
        Set JSON data to a text field.
        
        Args:
            field_name (str): Name of the field to store JSON data
            data (dict): Data to serialize as JSON
        """
        if data is not None:
            setattr(self, field_name, json.dumps(data))
        else:
            setattr(self, field_name, None)

# Import all model classes to ensure they are registered with SQLAlchemy
from .user import User
from .module import Module, Topic
from .exam import Exam, ExamSession
from .question import Question, Answer
from .progress import UserProgress, UserResponse

# List of all models for easy access
__all__ = [
    'BaseModel', 'TimestampMixin', 'JSONMixin',
    'User', 'Module', 'Topic', 'Exam', 'ExamSession', 
    'Question', 'Answer', 'UserProgress', 'UserResponse'
]

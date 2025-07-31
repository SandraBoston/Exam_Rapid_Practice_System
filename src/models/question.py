"""
Question and Answer models for PCEP Exam Accelerator.

Handles exam questions with multiple choice answers and rich content support.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from . import BaseModel

class Question(BaseModel):
    """
    Question model representing exam questions with rich content and metadata.
    """
    __tablename__ = 'questions'
    
    original_id = Column(String(50), index=True)  # Reference to source data
    text = Column(Text, nullable=False)
    html_content = Column(Text)  # Rich HTML content
    difficulty = Column(Integer, default=1, nullable=False, index=True)  # 1-5 scale
    topic_id = Column(Integer, ForeignKey('topics.id'), index=True)
    exam_id = Column(Integer, ForeignKey('exams.id'), nullable=False, index=True)
    code_snippet = Column(Text)  # Code examples or snippets
    explanation = Column(Text)  # Detailed explanation of the question
    question_order = Column(Integer, default=0, nullable=False, index=True)
    question_metadata = Column('metadata', Text, default='{}')  # JSON metadata for question types, multi-select, etc.
    
    # Enhanced metadata fields for source tracking
    source_exam_external_id = Column(Integer)  # Links to original exam's external ID
    original_question_number = Column(Integer)  # Original question number in source
    
    # Relationships
    topic = relationship("Topic", back_populates="questions")
    exam = relationship("Exam", back_populates="questions")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")
    user_responses = relationship("UserResponse", back_populates="question")
    
    def get_correct_answer(self):
        """
        Get the correct answer for this question.
        
        Returns:
            Answer: The correct answer object, or None if not found
        """
        for answer in self.answers:
            if answer.is_correct:
                return answer
        return None
    
    def get_incorrect_answers(self):
        """
        Get all incorrect answers for this question.
        
        Returns:
            list: List of incorrect Answer objects
        """
        return [answer for answer in self.answers if not answer.is_correct]
    
    def get_answers_ordered(self):
        """
        Get answers ordered by answer_order.
        
        Returns:
            list: Answers sorted by display order
        """
        return sorted(self.answers, key=lambda a: a.answer_order)
    
    def has_code_snippet(self):
        """
        Check if question contains a code snippet.
        
        Returns:
            bool: True if code snippet exists and is not empty
        """
        return bool(self.code_snippet and self.code_snippet.strip())
    
    def get_difficulty_label(self):
        """
        Get difficulty as a text label.
        
        Returns:
            str: Difficulty label (Beginner, Easy, Medium, Hard, Expert)
        """
        difficulty_labels = {
            1: "Beginner",
            2: "Easy", 
            3: "Medium",
            4: "Hard",
            5: "Expert"
        }
        return difficulty_labels.get(self.difficulty, "Unknown")
    
    def __repr__(self):
        return f"<Question(id={self.id}, exam='{self.exam.title if self.exam else None}', difficulty={self.difficulty})>"

class Answer(BaseModel):
    """
    Answer model representing multiple choice answers for questions.
    """
    __tablename__ = 'answers'
    
    original_id = Column(String(50), index=True)  # Reference to source data
    text = Column(Text, nullable=False)
    html_content = Column(Text)  # Rich HTML content
    is_correct = Column(Boolean, nullable=False, index=True)
    explanation = Column(Text)  # Explanation for why this answer is correct/incorrect
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False, index=True)
    answer_order = Column(Integer, default=0, nullable=False, index=True)
    
    # Relationships
    question = relationship("Question", back_populates="answers")
    user_responses = relationship("UserResponse", back_populates="answer")
    
    def get_correctness_label(self):
        """
        Get correctness as a text label.
        
        Returns:
            str: "Correct" or "Incorrect"
        """
        return "Correct" if self.is_correct else "Incorrect"
    
    def has_explanation(self):
        """
        Check if answer has an explanation.
        
        Returns:
            bool: True if explanation exists and is not empty
        """
        return bool(self.explanation and self.explanation.strip())
    
    def __repr__(self):
        return f"<Answer(id={self.id}, question_id={self.question_id}, is_correct={self.is_correct})>"

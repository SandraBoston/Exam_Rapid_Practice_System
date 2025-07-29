"""
Main application factory for the PCEP Exam Accelerator.
"""

from flask import Flask, render_template, jsonify
from flask_migrate import Migrate
from database import init_database, Base
# Task 19C: Import models for database integration
from models import User, Question, Answer, Exam, ExamSession, UserProgress, UserResponse
from models.module import Module as Topic
import os

# Global migrate instance
migrate = Migrate()

def create_app(config_name='default'):
    """
    Creates and configures the Flask application.

    Args:
        config_name (str): The configuration to use (e.g., 'development', 'testing').

    Returns:
        Flask: The configured Flask application instance.
    """
    app = Flask(__name__, instance_relative_config=True)
    
    # Configure the application
    configure_app(app, config_name)
    
    # Initialize database
    init_database(app)
    
    # Initialize Flask-Migrate
    migrate.init_app(app, Base)
    
    # Register CLI commands
    register_cli_commands(app)
    
    # Register routes
    register_routes(app, config_name)
    
    return app

def configure_app(app, config_name):
    """
    Configure the Flask application with appropriate settings.
    
    Args:
        app: Flask application instance
        config_name (str): Configuration environment name
    """
    # Default configuration
    app.config.update(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production'),
        # Use SQLALCHEMY_DATABASE_URI for Flask-SQLAlchemy and Flask-Migrate compatibility
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///instance/pcep_exam.db'),
        # Keep DATABASE_URL for backward compatibility
        DATABASE_URL=os.environ.get('DATABASE_URL', 'sqlite:///instance/pcep_exam.db'),
        SQLALCHEMY_ECHO=False,
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )
    
    # Environment-specific configuration
    if config_name == 'development':
        app.config.update(
            DEBUG=True,
            SQLALCHEMY_ECHO=True
        )
    elif config_name == 'testing':
        app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
            DATABASE_URL='sqlite:///:memory:',
            WTF_CSRF_ENABLED=False
        )
    elif config_name == 'production':
        app.config.update(
            DEBUG=False,
            SQLALCHEMY_ECHO=False
        )
        
        # Ensure secret key is set in production
        if app.config['SECRET_KEY'] == 'dev-secret-key-change-in-production':
            raise RuntimeError("Must set SECRET_KEY environment variable in production")

def register_cli_commands(app):
    """
    Register CLI commands for database management.
    
    Args:
        app: Flask application instance
    """
    @app.cli.command('init-db')
    def init_db_command():
        """Create database tables."""
        try:
            app.db_manager.create_all_tables()
            print("Database tables created successfully!")
        except Exception as e:
            print(f"Error creating database tables: {e}")
    
    @app.cli.command('drop-db')
    def drop_db_command():
        """Drop all database tables. Use with caution!"""
        try:
            app.db_manager.drop_all_tables()
            print("Database tables dropped successfully!")
        except Exception as e:
            print(f"Error dropping database tables: {e}")

def register_routes(app, config_name):
    """
    Register all application routes.
    
    Args:
        app: Flask application instance
        config_name: Configuration environment name
    """
    
    @app.route('/')
    def dashboard():
        """Main dashboard page"""
        # Sample data - would normally come from database
        stats = {
            'total_questions': 150,
            'completed_questions': 23,
            'success_rate': 78,
            'study_hours': 12
        }
        
        config = {
            'environment': config_name,
            'database_url': app.config.get('DATABASE_URL', 'Not configured')
        }
        
        return render_template('dashboard.html', stats=stats, config=config)
    
    @app.route('/practice')
    def practice_quiz():
        """Practice quiz page"""
        return render_template('practice_quiz.html')
    
    @app.route('/progress')
    def progress():
        """Progress tracking page"""
        # Sample progress data - would normally come from database
        progress_data = {
            'total_sessions': 5,
            'questions_attempted': 23,
            'average_score': 78,
            'study_streak': 3
        }
        
        return render_template('progress.html', progress=progress_data)
    
    @app.route('/health')
    def health_check():
        """System health check endpoint"""
        return jsonify({
            "status": "healthy", 
            "config": config_name,
            "database_configured": bool(app.config.get("DATABASE_URL")),
            "version": "1.0.0"
        })
    
    @app.route('/api/questions')
    def api_questions():
        """API endpoint to get practice questions from database"""
        try:
            # Task 19D: Replace hardcoded questions with database query
            print("Attempting database query...")
            
            # Get database session
            if not hasattr(app, 'db_manager'):
                raise Exception("Database manager not initialized")
            
            session = app.db_manager.get_session()
            print(f"Database session created: {session}")
            
            # Query questions from database with their answers
            db_questions = session.query(Question).order_by(Question.id).all()
            print(f"Found {len(db_questions)} questions in database")
            
            # Convert database questions to frontend format
            questions = []
            for db_q in db_questions:
                print(f"Processing question {db_q.id}: {db_q.text[:50]}...")
                
                # Get answers for this question
                answers = session.query(Answer).filter(Answer.question_id == db_q.id).order_by(Answer.id).all()
                print(f"  Found {len(answers)} answers")
                
                # Find correct answer index
                correct_index = 0
                answer_texts = []
                for i, answer in enumerate(answers):
                    answer_texts.append(answer.text)
                    if answer.is_correct:
                        correct_index = i
                
                # Convert to frontend format
                question_data = {
                    "id": db_q.id,
                    "question": db_q.text,
                    "options": answer_texts,
                    "correct": correct_index,
                    "explanation": db_q.explanation or "No explanation available.",
                    "topic": "Database Question",  # Simplified for now
                    "type": "single-select",
                    "required_answers": 1
                }
                questions.append(question_data)
            
            session.close()
            
            # If no questions in database, return empty array with message
            if not questions:
                print("No questions found in database")
                return jsonify({
                    "message": "No questions found in database. Please import exam data.",
                    "questions": []
                })
            
            print(f"Returning {len(questions)} questions from database")
            return jsonify(questions)
            
        except Exception as e:
            # Log the actual error and don't fall back silently
            print(f"❌ Database error: {e}")
            import traceback
            traceback.print_exc()
            
            # Return error message instead of hardcoded fallback
            return jsonify({
                "error": f"Database connection failed: {str(e)}",
                "message": "Unable to load questions from database", 
                "questions": []
            }), 500

    @app.route('/debug/question2')
    def debug_question2():
        """Debug endpoint specifically for Question 2"""
        questions = [
            {
                "id": 1,
                "question": "Which of the following is the correct way to create a comment in Python?",
                "options": [
                    "// This is a comment",
                    "/* This is a comment */",
                    "# This is a comment", 
                    "<!-- This is a comment -->"
                ],
                "correct": 2,
                "explanation": "In Python, single-line comments start with the # symbol.",
                "topic": "Python Fundamentals"
            },
            {
                "id": 2,
                "question": "What is the output of: print(type(5.0))?",
                "options": [
                    "<class 'int'>",
                    "<class 'float'>",
                    "<class 'str'>",
                    "<class 'decimal'>"
                ],
                "correct": 1,
                "explanation": "5.0 is a floating-point number, so its type is 'float'.",
                "topic": "Data Types"
            },
            {
                "id": 3,
                "question": "Which operator is used for integer division in Python?",
                "options": [
                    "/",
                    "//",
                    "%",
                    "**"
                ],
                "correct": 1,
                "explanation": "The // operator performs floor division (integer division).",
                "topic": "Operators"
            }
        ]
        
        # Return just Question 2 for debugging
        question2 = questions[1]  # Index 1 = Question 2
        return jsonify({
            "question2_data": question2,
            "options_count": len(question2["options"]),
            "options_detailed": [
                {"index": i, "text": opt, "length": len(opt)} 
                for i, opt in enumerate(question2["options"])
            ]
        })
    
if __name__ == '__main__':
    # For development/testing purposes
    app = create_app('development')
    app.run(host='localhost', port=5000, debug=True)

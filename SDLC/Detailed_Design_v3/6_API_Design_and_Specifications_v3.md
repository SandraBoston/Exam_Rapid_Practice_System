# 6. API Design and Specifications

## 6.1 RESTful API Architecture

The PCEP Certification Exam Accelerator implements a comprehensive RESTful API architecture that supports all system functionality while maintaining clean separation between the web interface and business logic. The API is designed for internal use by the web application and potential future extensions.

### 6.1.1 Resource Definitions

**Primary Resources:**
- **Exams**: Exam definitions and metadata
- **Questions**: Individual exam questions with answers
- **Sessions**: User exam sessions and progress
- **Users**: User accounts and preferences (future extension)
- **Topics**: Subject matter categories
- **Responses**: User answers and performance data

**Secondary Resources:**
- **Reports**: Performance analysis and statistics
- **Import/Export**: Data management operations
- **System**: Health checks and configuration

### 6.1.2 Endpoint Specifications

#### Base URL Structure
```
/api/v1/{resource}/{action}
```

**API Versioning**: Uses URL-based versioning (`/api/v1/`) to ensure backward compatibility for future enhancements.

### 6.1.3 Request/Response Formats

**Content Types:**
- Request: `application/json`
- Response: `application/json`
- File uploads: `multipart/form-data`

**Standard Response Format:**
```json
{
  "success": true,
  "data": { /* resource data */ },
  "message": "Operation completed successfully",
  "timestamp": "2025-06-20T10:30:00Z",
  "pagination": { /* pagination info if applicable */ }
}

{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "details": [ /* specific error details */ ]
  },
  "timestamp": "2025-06-20T10:30:00Z"
}
```

## 6.2 Internal API Modules

### 6.2.1 Exam API

**Purpose**: Manage exam definitions, questions, and metadata

#### Endpoints

**GET /api/v1/exams**
- **Purpose**: List all available exams with filtering and pagination
- **Parameters**:
  ```json
  {
    "page": 1,
    "limit": 20,
    "filter": {
      "difficulty": ["basic", "intermediate"],
      "topic": ["python_basics", "data_types"],
      "active": true
    },
    "sort": "created_at:desc"
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "data": {
      "exams": [
        {
          "id": 1,
          "title": "PCEP Practice Exam #1",
          "description": "Comprehensive Python basics assessment",
          "total_questions": 40,
          "time_limit": 3600,
          "difficulty": "basic",
          "topics": ["python_basics", "data_types", "control_flow"],
          "created_at": "2025-06-15T09:00:00Z",
          "updated_at": "2025-06-15T09:00:00Z",
          "is_active": true,
          "metadata": {
            "source": "official_pcep_prep",
            "version": "1.0"
          }
        }
      ]
    },
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 5,
      "pages": 1
    }
  }
  ```

**GET /api/v1/exams/{id}**
- **Purpose**: Get detailed exam information
- **Response**: Complete exam data including question count by topic

**POST /api/v1/exams**
- **Purpose**: Create a new exam
- **Request Body**:
  ```json
  {
    "title": "Custom Practice Exam",
    "description": "User-created exam for focused practice",
    "time_limit": 2400,
    "questions": [1, 5, 10, 15, 20],
    "configuration": {
      "randomize_questions": true,
      "randomize_answers": false,
      "allow_review": true
    }
  }
  ```

**PUT /api/v1/exams/{id}**
- **Purpose**: Update exam metadata and configuration
- **Request Body**: Partial exam data for updates

**DELETE /api/v1/exams/{id}**
- **Purpose**: Deactivate an exam (soft delete)
- **Response**: Confirmation of deactivation

**GET /api/v1/exams/{id}/questions**
- **Purpose**: Get all questions for a specific exam
- **Parameters**:
  ```json
  {
    "include_answers": false,
    "shuffle": false,
    "limit": null
  }
  ```
- **Response**: Array of question objects with optional answer data

### 6.2.2 Session API

**Purpose**: Manage user exam sessions, progress tracking, and state persistence

#### Endpoints

**GET /api/v1/sessions**
- **Purpose**: List user's exam sessions with filtering
- **Parameters**:
  ```json
  {
    "status": ["active", "completed", "paused"],
    "exam_id": 1,
    "date_range": {
      "start": "2025-06-01T00:00:00Z",
      "end": "2025-06-20T23:59:59Z"
    }
  }
  ```

**POST /api/v1/sessions**
- **Purpose**: Create a new exam session
- **Request Body**:
  ```json
  {
    "exam_id": 1,
    "session_type": "practice",
    "configuration": {
      "time_limit": 3600,
      "randomize_questions": true,
      "immediate_feedback": true,
      "topic_filter": ["python_basics"],
      "difficulty_filter": [1, 2, 3],
      "question_count": 20
    }
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "data": {
      "session": {
        "id": "sess_123456",
        "exam_id": 1,
        "start_time": "2025-06-20T10:30:00Z",
        "time_limit": 3600,
        "configuration": { /* session config */ },
        "status": "active",
        "current_question": 1,
        "total_questions": 20,
        "progress": {
          "answered": 0,
          "bookmarked": 0,
          "skipped": 0
        }
      }
    }
  }
  ```

**GET /api/v1/sessions/{id}**
- **Purpose**: Get detailed session information and current state
- **Response**: Complete session data including current question and progress

**PUT /api/v1/sessions/{id}**
- **Purpose**: Update session state (pause, resume, extend time)
- **Request Body**:
  ```json
  {
    "action": "pause",
    "reason": "user_requested",
    "additional_time": 0
  }
  ```

**POST /api/v1/sessions/{id}/responses**
- **Purpose**: Submit an answer for the current question
- **Request Body**:
  ```json
  {
    "question_id": 1,
    "answer_ids": [3],
    "time_taken": 45.5,
    "confidence_level": 3,
    "is_bookmarked": false,
    "is_skipped": false
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "data": {
      "response_recorded": true,
      "is_correct": true,
      "immediate_feedback": {
        "explanation": "Correct! Lists are mutable...",
        "reference_links": ["docs.python.org/..."]
      },
      "session_progress": {
        "current_question": 2,
        "answered": 1,
        "score_so_far": 100,
        "time_remaining": 3555
      }
    }
  }
  ```

**GET /api/v1/sessions/{id}/question/{number}**
- **Purpose**: Get a specific question in the session
- **Response**: Question data with session-specific context

**POST /api/v1/sessions/{id}/complete**
- **Purpose**: Complete the exam session and calculate final results
- **Response**: Comprehensive session results and analysis

**GET /api/v1/sessions/{id}/results**
- **Purpose**: Get session results and performance analysis
- **Response**: Detailed results with charts data and recommendations

### 6.2.3 Data Management API

**Purpose**: Handle import, export, and conversion of exam data

#### Endpoints

**POST /api/v1/data/import**
- **Purpose**: Import exam data from various formats
- **Content-Type**: `multipart/form-data`
- **Request**:
  ```
  file: [uploaded file]
  format: "html" | "json" | "auto"
  options: {
    "validate_questions": true,
    "check_duplicates": true,
    "auto_categorize": true
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "data": {
      "import_id": "imp_789012",
      "status": "processing",
      "file_info": {
        "filename": "pcep_questions.html",
        "size": 245760,
        "format": "html"
      },
      "estimated_completion": "2025-06-20T10:35:00Z"
    }
  }
  ```

**GET /api/v1/data/import/{id}/status**
- **Purpose**: Check import progress and results
- **Response**:
  ```json
  {
    "success": true,
    "data": {
      "import_id": "imp_789012",
      "status": "completed",
      "progress": 100,
      "results": {
        "questions_imported": 40,
        "questions_skipped": 2,
        "validation_errors": 0,
        "warnings": 1,
        "exam_created": {
          "id": 5,
          "title": "Imported Exam from pcep_questions.html"
        }
      },
      "logs": [
        {
          "level": "warning",
          "message": "Question 15 has unclear wording",
          "timestamp": "2025-06-20T10:33:00Z"
        }
      ]
    }
  }
  ```

**GET /api/v1/data/export/{exam_id}**
- **Purpose**: Export exam data in various formats
- **Parameters**:
  ```json
  {
    "format": "json",
    "include_answers": true,
    "include_explanations": true,
    "include_metadata": true
  }
  ```
- **Response**: File download or structured data

**POST /api/v1/data/convert**
- **Purpose**: Convert between data formats without importing
- **Request Body**: File data and conversion options
- **Response**: Converted data or download link

### 6.2.4 User Management API

**Purpose**: Manage user preferences and progress tracking (future extension)

#### Endpoints

**GET /api/v1/users/profile**
- **Purpose**: Get current user profile and preferences
- **Response**: User data with progress statistics

**PUT /api/v1/users/profile**
- **Purpose**: Update user preferences and settings
- **Request Body**: Partial user data for updates

**GET /api/v1/users/progress**
- **Purpose**: Get comprehensive user progress across all topics
- **Response**: Progress data with topic breakdown and trends

### 6.2.5 Reporting API

**Purpose**: Generate performance reports and analytics

#### Endpoints

**GET /api/v1/reports/performance**
- **Purpose**: Get user performance analytics
- **Parameters**:
  ```json
  {
    "time_range": "30d",
    "group_by": "topic",
    "include_trends": true,
    "format": "summary"
  }
  ```
- **Response**: Structured performance data for visualization

**GET /api/v1/reports/session/{id}**
- **Purpose**: Get detailed session report
- **Response**: Comprehensive session analysis with recommendations

**POST /api/v1/reports/custom**
- **Purpose**: Generate custom reports with specific criteria
- **Request Body**: Report configuration and filters
- **Response**: Generated report data

## 6.3 API Security

### 6.3.1 Authentication Mechanisms

**Session-Based Authentication**: Uses Flask sessions for web application authentication
```python
@require_authentication
def api_endpoint():
    current_user = get_current_user()
    # API logic
```

**API Key Authentication** (future extension):
```python
@require_api_key
def api_endpoint():
    api_client = get_api_client()
    # API logic
```

### 6.3.2 Authorization Rules

**Role-Based Access Control**:
- **User**: Access to own sessions, exams, and progress data
- **Admin**: Full access to all data and management functions
- **System**: Internal API access for background processes

### 6.3.3 Input Validation

**Request Validation Middleware**:
```python
from marshmallow import Schema, fields, validate

class CreateSessionSchema(Schema):
    exam_id = fields.Integer(required=True, validate=validate.Range(min=1))
    session_type = fields.String(required=True, validate=validate.OneOf(['practice', 'exam']))
    configuration = fields.Dict(missing={})
    
@validate_request(CreateSessionSchema())
def create_session():
    # Validated request data available
    pass
```

**Data Sanitization**:
- HTML content sanitization for user inputs
- SQL injection prevention through ORM
- JSON schema validation for all endpoints

## 6.4 External Integrations

The system is designed for offline operation and does not require external API dependencies for core functionality. However, the architecture supports future integrations:

### 6.4.1 Potential Future Integrations

**Learning Management Systems (LMS)**:
- Grade passback APIs
- Single Sign-On (SSO) integration
- Progress synchronization

**Python.org Resources**:
- Documentation links
- Official tutorial references
- Community resource integration

**Analytics Services**:
- Usage analytics
- Performance monitoring
- Error tracking

### 6.4.2 Webhook Support

**Event Notifications** (future extension):
```python
# Webhook configuration
webhooks = {
    'session_completed': 'https://lms.example.com/api/grades',
    'import_finished': 'https://admin.example.com/api/notifications'
}

# Event publishing
def publish_webhook_event(event_type, data):
    webhook_url = webhooks.get(event_type)
    if webhook_url:
        requests.post(webhook_url, json=data)
```

## 6.5 API Documentation

### 6.5.1 Interactive Documentation

**Swagger/OpenAPI Integration**:
```python
from flask_restx import Api, Resource, fields

api = Api(app, version='1.0', title='PCEP Exam API',
          description='API for PCEP Certification Exam Accelerator')

session_model = api.model('Session', {
    'id': fields.String(required=True, description='Session ID'),
    'exam_id': fields.Integer(required=True, description='Exam ID'),
    'status': fields.String(required=True, description='Session status')
})

@api.route('/sessions')
class SessionList(Resource):
    @api.marshal_list_with(session_model)
    def get(self):
        """Get all sessions for current user"""
        return get_user_sessions()
```

### 6.5.2 Documentation Standards

**Endpoint Documentation Requirements**:
- Purpose and use case description
- Complete parameter specifications
- Request/response examples
- Error scenarios and codes
- Rate limiting information
- Authentication requirements

**API Versioning Strategy**:
- Semantic versioning for API releases
- Backward compatibility maintenance
- Deprecation notice procedures
- Migration guides for version updates

This comprehensive API design provides a robust foundation for the PCEP Certification Exam Accelerator's functionality while maintaining flexibility for future enhancements and integrations.

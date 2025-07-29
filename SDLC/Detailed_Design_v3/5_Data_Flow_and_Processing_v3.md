# 5. Data Flow and Processing

## 5.1 Data Flow Diagrams

### 5.1.1 Exam Data Import Flow

The following diagram shows the complete process for importing exam data from external sources into the system:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   HTML/JSON     │────▶│ Data Extraction │────▶│  Data Parsing   │
│  Source Files   │     │    Module       │     │ & Normalization │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                        │                        │
         │                        ▼                        ▼
         │               ┌─────────────────┐     ┌─────────────────┐
         │               │  File System    │     │   JSON Object   │
         │               │   Validation    │     │   Validation    │
         │               └─────────────────┘     └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Error Report   │     │   Processing    │     │ Data Structure  │
│  & Logging      │◄────│    Status       │     │  Transformation │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                 │                        │
                                 ▼                        ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │ Quality Control │     │  ID Assignment  │
                        │  & Validation   │     │ & Categorization│
                        └─────────────────┘     └─────────────────┘
                                 │                        │
                                 ▼                        ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   Database      │◄────│   Database      │
                        │   Transaction   │     │   Storage       │
                        └─────────────────┘     └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │    Success      │
                        │   Confirmation  │
                        └─────────────────┘
```

### 5.1.2 Exam Session Flow

This diagram illustrates the complete user workflow during an exam session:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  User Login &   │────▶│  Exam Selection │────▶│ Session Init &  │
│ Authentication  │     │   & Setup       │     │ Timer Start     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                          │
                                                          ▼
                                                ┌─────────────────┐
                                                │  Load First     │
                                                │   Question      │
                                                └─────────────────┘
                                                          │
                        ┌─────────────────────────────────┴─────────────────────────────────┐
                        │                    Question Display Loop                        │
                        │                                                                 │
                        ▼                                                                 │
              ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐       │
              │  Display        │────▶│  User Answer    │────▶│   Process &     │       │
              │  Question       │     │   Selection     │     │ Validate Answer │       │
              └─────────────────┘     └─────────────────┘     └─────────────────┘       │
                        ▲                                               │               │
                        │                                               ▼               │
              ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐       │
              │   Navigation    │◄────│    Session      │◄────│   Update        │       │
              │ (Next/Previous) │     │  State Update   │     │ Progress & Time │       │
              └─────────────────┘     └─────────────────┘     └─────────────────┘       │
                        │                                               │               │
                        └───────────────────┬───────────────────────────┘               │
                                           │                                           │
                                           ▼                                           │
                              ┌─────────────────┐                                      │
                              │   More          │ Yes ─────────────────────────────────┘
                              │ Questions?      │
                              └─────────────────┘
                                           │ No
                                           ▼
                              ┌─────────────────┐     ┌─────────────────┐
                              │  Session End &  │────▶│ Score Calculation│
                              │ Timer Stop      │     │  & Analysis     │
                              └─────────────────┘     └─────────────────┘
                                                               │
                                                               ▼
                                                    ┌─────────────────┐
                                                    │  Results Display│
                                                    │  & Reporting    │
                                                    └─────────────────┘
```

## 5.2 Data Processing Flows

### 5.2.1 HTML to JSON Conversion Process

The HTML to JSON conversion process is critical for importing exam data from external sources. This process handles various HTML formats and extracts structured data reliably.

#### Algorithm Overview

**Phase 1: HTML Preprocessing**
1. **File Loading and Validation**
   - Load HTML content from input file
   - Verify file integrity and encoding
   - Sanitize HTML to handle encoding issues
   - Normalize line endings and whitespace

2. **Structure Analysis**
   - Parse HTML DOM structure using BeautifulSoup
   - Verify basic HTML document integrity
   - Identify potential data-containing sections

**Phase 2: Data Extraction**
1. **Script Tag Identification**
   ```python
   # Primary extraction pattern
   pattern_primary = r'let\s+data\s*=\s*({.*?});'
   
   # Alternative patterns for different formats
   pattern_alt1 = r'var\s+examData\s*=\s*({.*?});'
   pattern_alt2 = r'window\.examData\s*=\s*({.*?});'
   ```

2. **JSON Data Extraction**
   - Search for script tags containing exam data
   - Apply multiple extraction patterns sequentially
   - Handle JavaScript-specific syntax cleanup
   - Validate extracted content as valid JSON

3. **Content Validation**
   - Parse extracted JSON string into object
   - Validate against expected schema structure
   - Check for required fields (questions, answers, metadata)
   - Verify data type consistency

**Phase 3: Data Transformation**
1. **Structure Normalization**
   ```python
   def normalize_question_structure(question_data):
       normalized = {
           'id': question_data.get('id') or generate_unique_id(),
           'text': clean_text(question_data.get('question', '')),
           'type': determine_question_type(question_data),
           'difficulty': assess_difficulty(question_data),
           'topic': extract_topic_tags(question_data),
           'code_snippet': extract_code_blocks(question_data),
           'answers': normalize_answers(question_data.get('answers', []))
       }
       return normalized
   ```

2. **Data Enrichment**
   - Generate unique system IDs for questions and answers
   - Extract and parse code blocks with syntax validation
   - Assign topic categories based on content analysis
   - Calculate estimated difficulty levels
   - Add metadata (import timestamp, source file reference)

**Phase 4: Quality Assurance**
1. **Data Integrity Checks**
   - Verify all questions have corresponding answers
   - Ensure at least one correct answer per question
   - Check for duplicate questions or answers
   - Validate question-answer relationship consistency

2. **Content Quality Assessment**
   - Verify code snippets compile and run correctly
   - Check answer option plausibility
   - Assess question clarity and completeness
   - Generate quality metrics and warnings

#### Error Handling Strategy

**Graceful Degradation**:
- If primary extraction fails, attempt alternative patterns
- Provide partial extraction with clear error reporting
- Maintain detailed logs of extraction issues
- Allow manual review and correction of problematic data

**Common Error Scenarios**:
```python
class ExtractionError(Exception):
    def __init__(self, error_type, message, data=None):
        self.error_type = error_type
        self.message = message
        self.problematic_data = data

# Error types:
# - INVALID_HTML: Malformed HTML structure
# - NO_DATA_FOUND: No matching script tags
# - INVALID_JSON: JSON parsing errors
# - SCHEMA_MISMATCH: Data doesn't match expected structure
# - INCOMPLETE_DATA: Missing required fields
```

### 5.2.2 Question Answer Analysis Process

The question analysis process enhances imported data with intelligent categorization, quality assessment, and metadata generation.

#### Analysis Components

**1. Question Type Classification**
```python
def classify_question_type(question_text, answers):
    # Analyze question structure and content
    if contains_code_block(question_text):
        if asks_for_output(question_text):
            return 'CODE_OUTPUT'
        elif asks_for_completion(question_text):
            return 'CODE_COMPLETION'
        else:
            return 'CODE_ANALYSIS'
    
    # Count correct answers to determine type
    correct_count = sum(1 for answer in answers if answer.get('is_correct'))
    
    if correct_count == 1:
        return 'SINGLE_CHOICE'
    elif correct_count > 1:
        return 'MULTIPLE_CHOICE'
    else:
        return 'UNSPECIFIED'  # Flag for review
```

**2. Difficulty Assessment**
```python
def assess_difficulty(question_data):
    difficulty_factors = {
        'concept_complexity': analyze_concept_complexity(question_data['text']),
        'code_complexity': analyze_code_complexity(question_data.get('code_snippet')),
        'answer_similarity': calculate_answer_similarity(question_data['answers']),
        'required_knowledge': assess_prerequisite_knowledge(question_data)
    }
    
    # Weighted scoring algorithm
    weights = {'concept_complexity': 0.4, 'code_complexity': 0.3, 
               'answer_similarity': 0.2, 'required_knowledge': 0.1}
    
    weighted_score = sum(difficulty_factors[factor] * weights[factor] 
                        for factor in weights)
    
    # Convert to 1-5 scale
    return min(5, max(1, round(weighted_score * 5)))
```

**3. Topic Categorization**
```python
def categorize_by_topic(question_content):
    topic_keywords = {
        'python_basics': ['variable', 'print', 'input', 'type', 'string', 'integer'],
        'data_types': ['list', 'tuple', 'dict', 'set', 'string', 'int', 'float'],
        'control_flow': ['if', 'else', 'elif', 'for', 'while', 'break', 'continue'],
        'functions': ['def', 'return', 'parameter', 'argument', 'lambda'],
        'modules': ['import', 'from', 'module', 'package', '__name__'],
        'exceptions': ['try', 'except', 'finally', 'raise', 'exception'],
        'file_operations': ['open', 'read', 'write', 'close', 'file'],
        'oop': ['class', 'object', 'method', 'attribute', 'inheritance']
    }
    
    content_lower = question_content.lower()
    topic_scores = {}
    
    for topic, keywords in topic_keywords.items():
        score = sum(content_lower.count(keyword) for keyword in keywords)
        if score > 0:
            topic_scores[topic] = score
    
    # Return top topics with confidence scores
    return sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
```

**4. Quality Metrics Calculation**
```python
def calculate_quality_metrics(question_data):
    metrics = {
        'clarity_score': assess_question_clarity(question_data['text']),
        'answer_quality': assess_answer_options(question_data['answers']),
        'code_validity': validate_code_snippets(question_data.get('code_snippet')),
        'completeness': check_question_completeness(question_data),
        'uniqueness': check_question_uniqueness(question_data)
    }
    
    # Flag questions that need review
    review_flags = []
    if metrics['clarity_score'] < 0.7:
        review_flags.append('unclear_wording')
    if metrics['answer_quality'] < 0.6:
        review_flags.append('poor_distractors')
    if not metrics['code_validity']:
        review_flags.append('invalid_code')
    
    metrics['review_flags'] = review_flags
    metrics['overall_quality'] = calculate_weighted_average(metrics)
    
    return metrics
```

## 5.3 User Session Workflows

### 5.3.1 Session Creation

The session creation process establishes the framework for tracking user progress and performance throughout an exam.

#### Session Initialization Steps

**1. Pre-Session Validation**
```python
def initialize_exam_session(user_id, exam_id, session_config):
    # Validate prerequisites
    user = validate_user_access(user_id)
    exam = validate_exam_availability(exam_id)
    
    # Check for existing incomplete sessions
    existing_session = get_incomplete_session(user_id, exam_id)
    if existing_session and session_config.get('resume_allowed'):
        return resume_session(existing_session)
    
    # Create new session
    session = ExamSession(
        user_id=user_id,
        exam_id=exam_id,
        start_time=datetime.utcnow(),
        time_limit=exam.time_limit,
        session_type=session_config.get('type', 'practice'),
        configuration=session_config
    )
    
    # Initialize session state
    session.questions = prepare_question_sequence(exam, session_config)
    session.current_question_index = 0
    session.responses = {}
    session.bookmarked_questions = set()
    
    return session
```

**2. Question Sequence Preparation**
```python
def prepare_question_sequence(exam, config):
    questions = get_exam_questions(exam.id)
    
    # Apply filtering based on configuration
    if config.get('topic_filter'):
        questions = filter_by_topics(questions, config['topic_filter'])
    
    if config.get('difficulty_filter'):
        questions = filter_by_difficulty(questions, config['difficulty_filter'])
    
    # Apply randomization if requested
    if config.get('randomize_questions'):
        random.shuffle(questions)
    
    # Limit number of questions if specified
    if config.get('question_limit'):
        questions = questions[:config['question_limit']]
    
    return questions
```

### 5.3.2 Question Navigation

Navigation management maintains session state while allowing flexible movement through the exam.

#### Navigation State Management
```python
class NavigationManager:
    def __init__(self, session):
        self.session = session
        self.current_index = 0
        self.navigation_history = []
    
    def next_question(self):
        if self.current_index < len(self.session.questions) - 1:
            self.navigation_history.append(self.current_index)
            self.current_index += 1
            return self.get_current_question()
        return None
    
    def previous_question(self):
        if self.navigation_history:
            self.current_index = self.navigation_history.pop()
            return self.get_current_question()
        return None
    
    def jump_to_question(self, question_index):
        if 0 <= question_index < len(self.session.questions):
            self.navigation_history.append(self.current_index)
            self.current_index = question_index
            return self.get_current_question()
        return None
    
    def get_navigation_state(self):
        return {
            'current_index': self.current_index,
            'total_questions': len(self.session.questions),
            'can_go_previous': bool(self.navigation_history),
            'can_go_next': self.current_index < len(self.session.questions) - 1,
            'progress_percentage': (self.current_index + 1) / len(self.session.questions) * 100
        }
```

### 5.3.3 Answer Processing

Answer processing handles user input validation, scoring, and immediate feedback generation.

#### Real-time Answer Processing
```python
def process_user_answer(session, question_id, user_response):
    question = get_question_by_id(question_id)
    answer_start_time = time.time()
    
    # Validate response format
    if not validate_response_format(user_response, question.question_type):
        raise ValueError("Invalid response format for question type")
    
    # Calculate time taken
    time_taken = answer_start_time - session.question_start_time
    
    # Evaluate correctness
    is_correct, explanation = evaluate_answer(question, user_response)
    
    # Store response
    response_record = UserResponse(
        session_id=session.id,
        question_id=question_id,
        user_answer=user_response,
        is_correct=is_correct,
        time_taken=time_taken,
        timestamp=datetime.utcnow()
    )
    
    # Update session statistics
    session.update_progress(is_correct, time_taken)
    
    # Generate immediate feedback if in practice mode
    feedback = None
    if session.session_type == 'practice':
        feedback = generate_immediate_feedback(question, user_response, is_correct, explanation)
    
    return {
        'response_recorded': True,
        'is_correct': is_correct,
        'time_taken': time_taken,
        'feedback': feedback,
        'session_progress': session.get_progress_summary()
    }
```

#### Answer Evaluation Algorithm
```python
def evaluate_answer(question, user_response):
    correct_answers = get_correct_answers(question.id)
    
    if question.question_type == 'SINGLE_CHOICE':
        is_correct = user_response in [ans.id for ans in correct_answers]
        explanation = get_answer_explanation(user_response)
        
    elif question.question_type == 'MULTIPLE_CHOICE':
        correct_ids = set(ans.id for ans in correct_answers)
        user_ids = set(user_response)
        is_correct = correct_ids == user_ids
        explanation = generate_multiple_choice_explanation(correct_ids, user_ids)
        
    elif question.question_type == 'CODE_OUTPUT':
        expected_output = get_expected_code_output(question.code_snippet)
        is_correct = normalize_output(user_response) == normalize_output(expected_output)
        explanation = generate_code_explanation(question.code_snippet, expected_output, user_response)
    
    return is_correct, explanation
```

### 5.3.4 Session Completion

Session completion triggers comprehensive scoring, analysis, and report generation.

#### Completion Processing Pipeline
```python
def complete_exam_session(session):
    # Finalize session timing
    session.end_time = datetime.utcnow()
    session.total_time = (session.end_time - session.start_time).total_seconds()
    session.is_completed = True
    
    # Calculate comprehensive scores
    scoring_results = calculate_session_scores(session)
    
    # Generate performance analysis
    performance_analysis = analyze_session_performance(session, scoring_results)
    
    # Update user progress tracking
    update_user_progress(session.user_id, performance_analysis)
    
    # Generate detailed report
    session_report = generate_session_report(session, scoring_results, performance_analysis)
    
    # Store all results
    save_session_completion_data(session, scoring_results, performance_analysis, session_report)
    
    return {
        'session_id': session.id,
        'scores': scoring_results,
        'analysis': performance_analysis,
        'report': session_report,
        'recommendations': generate_study_recommendations(performance_analysis)
    }
```

#### Performance Analysis Algorithm
```python
def analyze_session_performance(session, scoring_results):
    responses = get_session_responses(session.id)
    
    analysis = {
        'overall_performance': {
            'score_percentage': scoring_results['percentage'],
            'time_efficiency': calculate_time_efficiency(session),
            'completion_rate': calculate_completion_rate(session)
        },
        'topic_breakdown': calculate_topic_performance(responses),
        'difficulty_analysis': calculate_difficulty_performance(responses),
        'question_type_analysis': calculate_question_type_performance(responses),
        'time_analysis': {
            'average_time_per_question': session.total_time / len(responses),
            'time_distribution': calculate_time_distribution(responses),
            'rushed_questions': identify_rushed_questions(responses),
            'slow_questions': identify_slow_questions(responses)
        },
        'pattern_analysis': {
            'answer_patterns': analyze_answer_patterns(responses),
            'common_mistakes': identify_common_mistakes(responses),
            'strengths': identify_performance_strengths(responses),
            'weaknesses': identify_performance_weaknesses(responses)
        }
    }
    
    return analysis
```

## 5.4 Data Validation and Quality Control

### 5.4.1 Import Validation Pipeline

```python
class DataValidationPipeline:
    def __init__(self):
        self.validators = [
            SchemaValidator(),
            ContentValidator(),
            RelationshipValidator(),
            QualityValidator()
        ]
    
    def validate_imported_data(self, data):
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'metrics': {}
        }
        
        for validator in self.validators:
            result = validator.validate(data)
            validation_results['errors'].extend(result.get('errors', []))
            validation_results['warnings'].extend(result.get('warnings', []))
            validation_results['metrics'].update(result.get('metrics', {}))
            
            if result.get('is_valid', True) is False:
                validation_results['is_valid'] = False
        
        return validation_results
```

### 5.4.2 Real-time Data Monitoring

```python
class SessionDataMonitor:
    def __init__(self):
        self.anomaly_detectors = [
            ResponseTimeAnomalyDetector(),
            AnswerPatternDetector(),
            SessionBehaviorDetector()
        ]
    
    def monitor_session_data(self, session, new_response):
        monitoring_results = []
        
        for detector in self.anomaly_detectors:
            anomaly_result = detector.check_anomaly(session, new_response)
            if anomaly_result.get('anomaly_detected'):
                monitoring_results.append(anomaly_result)
        
        return monitoring_results
```

This comprehensive data flow and processing design ensures reliable data import, efficient session management, and intelligent analysis of user performance, providing a solid foundation for the PCEP Certification Exam Accelerator's core functionality.

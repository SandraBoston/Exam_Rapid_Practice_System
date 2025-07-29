# 7. Security Architecture

## 7.1 Authentication System

The PCEP Certification Exam Accelerator implements a comprehensive security framework designed to protect user data, ensure session integrity, and prevent common web application vulnerabilities while maintaining usability for offline operation.

### 7.1.1 Login Process

**Multi-Factor Authentication Flow**:
```python
class AuthenticationService:
    def authenticate_user(self, username, password, remember_me=False):
        # Phase 1: Basic credential validation
        user = self.validate_credentials(username, password)
        if not user:
            self.log_failed_attempt(username, request.remote_addr)
            raise AuthenticationError("Invalid credentials")
        
        # Phase 2: Account status checks
        if not user.is_active:
            raise AuthenticationError("Account is disabled")
        
        if user.is_locked:
            remaining_time = user.get_lockout_remaining_time()
            raise AuthenticationError(f"Account locked for {remaining_time} minutes")
        
        # Phase 3: Session creation
        session_token = self.create_secure_session(user, remember_me)
        
        # Phase 4: Security logging
        self.log_successful_login(user, request.remote_addr)
        user.update_last_login()
        
        return {
            'user': user,
            'session_token': session_token,
            'session_expires': self.calculate_session_expiry(remember_me)
        }
    
    def validate_credentials(self, username, password):
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            return user
        return None
```

**Password Security Standards**:
- **Hashing**: bcrypt with configurable cost factor (minimum 12)
- **Complexity Requirements**: Minimum 8 characters, mix of character types
- **Password History**: Prevent reuse of last 5 passwords
- **Strength Validation**: Real-time strength assessment during creation

```python
class PasswordManager:
    def hash_password(self, password):
        salt_rounds = current_app.config.get('BCRYPT_ROUNDS', 12)
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=salt_rounds))
    
    def validate_password_strength(self, password):
        requirements = {
            'min_length': len(password) >= 8,
            'has_uppercase': any(c.isupper() for c in password),
            'has_lowercase': any(c.islower() for c in password),
            'has_digit': any(c.isdigit() for c in password),
            'has_special': any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password),
            'not_common': password not in self.get_common_passwords()
        }
        return requirements
```

### 7.1.2 Session Management

**Secure Session Implementation**:
```python
class SessionManager:
    def create_secure_session(self, user, remember_me=False):
        session_data = {
            'user_id': user.id,
            'username': user.username,
            'login_time': datetime.utcnow().isoformat(),
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent'),
            'csrf_token': self.generate_csrf_token()
        }
        
        # Set session expiry
        if remember_me:
            session.permanent = True
            current_app.permanent_session_lifetime = timedelta(days=30)
        else:
            session.permanent = False
            current_app.permanent_session_lifetime = timedelta(hours=8)
        
        # Store encrypted session data
        session['user_data'] = self.encrypt_session_data(session_data)
        session['session_id'] = self.generate_session_id()
        
        return session['session_id']
    
    def validate_session(self, required_permissions=None):
        if 'user_data' not in session:
            raise SessionError("No active session")
        
        try:
            session_data = self.decrypt_session_data(session['user_data'])
        except DecryptionError:
            self.clear_session()
            raise SessionError("Invalid session data")
        
        # Validate session integrity
        if not self.validate_session_integrity(session_data):
            self.clear_session()
            raise SessionError("Session integrity compromised")
        
        # Check permissions if required
        if required_permissions:
            user = User.query.get(session_data['user_id'])
            if not user.has_permissions(required_permissions):
                raise PermissionError("Insufficient permissions")
        
        return session_data
```

**Session Security Features**:
- **Session Rotation**: New session ID on privilege escalation
- **Concurrent Session Limiting**: Maximum 3 active sessions per user
- **Idle Timeout**: Automatic logout after 30 minutes of inactivity
- **IP Binding**: Session tied to originating IP address
- **Secure Cookies**: HTTPOnly, Secure, SameSite attributes

### 7.1.3 Password Policies

**Account Security Policies**:
```python
class AccountSecurityPolicy:
    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_DURATION = timedelta(minutes=15)
    PASSWORD_EXPIRY = timedelta(days=90)
    
    def enforce_failed_login_policy(self, username):
        attempts = self.get_failed_attempts(username)
        if attempts >= self.MAX_FAILED_ATTEMPTS:
            self.lock_account(username, self.LOCKOUT_DURATION)
            self.notify_security_event('account_locked', {'username': username})
    
    def check_password_expiry(self, user):
        if user.password_changed_at:
            age = datetime.utcnow() - user.password_changed_at
            if age > self.PASSWORD_EXPIRY:
                return {'expired': True, 'days_overdue': age.days - 90}
        return {'expired': False}
```

## 7.2 Authorization Framework

### 7.2.1 Role Definitions

**Role-Based Access Control (RBAC)**:
```python
class Role:
    ANONYMOUS = 'anonymous'
    USER = 'user'
    ADMIN = 'admin'
    SYSTEM = 'system'

class Permission:
    # Exam permissions
    VIEW_EXAMS = 'exam:view'
    TAKE_EXAMS = 'exam:take'
    CREATE_EXAMS = 'exam:create'
    MANAGE_EXAMS = 'exam:manage'
    
    # Session permissions
    VIEW_OWN_SESSIONS = 'session:view:own'
    VIEW_ALL_SESSIONS = 'session:view:all'
    MANAGE_SESSIONS = 'session:manage'
    
    # Data permissions
    IMPORT_DATA = 'data:import'
    EXPORT_DATA = 'data:export'
    MANAGE_DATA = 'data:manage'
    
    # System permissions
    VIEW_SYSTEM_INFO = 'system:view'
    MANAGE_SYSTEM = 'system:manage'

ROLE_PERMISSIONS = {
    Role.ANONYMOUS: [],
    Role.USER: [
        Permission.VIEW_EXAMS,
        Permission.TAKE_EXAMS,
        Permission.VIEW_OWN_SESSIONS,
        Permission.EXPORT_DATA
    ],
    Role.ADMIN: [
        # All user permissions plus:
        Permission.CREATE_EXAMS,
        Permission.MANAGE_EXAMS,
        Permission.VIEW_ALL_SESSIONS,
        Permission.MANAGE_SESSIONS,
        Permission.IMPORT_DATA,
        Permission.MANAGE_DATA,
        Permission.VIEW_SYSTEM_INFO,
        Permission.MANAGE_SYSTEM
    ]
}
```

### 7.2.2 Permission Checks

**Decorator-Based Authorization**:
```python
from functools import wraps

def require_permission(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                session_data = session_manager.validate_session([permission])
            except (SessionError, PermissionError) as e:
                if request.is_json:
                    return jsonify({'error': str(e)}), 403
                else:
                    flash('Access denied: ' + str(e), 'error')
                    return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Usage examples
@require_permission(Permission.MANAGE_EXAMS)
def admin_exam_management():
    return render_template('admin/exams.html')

@require_permission(Permission.TAKE_EXAMS)
def start_exam_session():
    # Exam session logic
    pass
```

**Resource-Level Authorization**:
```python
class ResourceAuthorization:
    def can_access_session(self, user, session):
        # Users can access their own sessions
        if session.user_id == user.id:
            return True
        
        # Admins can access all sessions
        if user.has_role(Role.ADMIN):
            return True
        
        return False
    
    def can_modify_exam(self, user, exam):
        # Check if user is exam creator or admin
        return (exam.created_by == user.id or 
                user.has_permission(Permission.MANAGE_EXAMS))
```

## 7.3 Data Protection

### 7.3.1 Sensitive Data Handling

**Data Classification and Protection**:
```python
class DataProtection:
    SENSITIVE_FIELDS = {
        'password_hash': 'HIGH',
        'session_data': 'HIGH',
        'personal_info': 'MEDIUM',
        'performance_data': 'LOW'
    }
    
    def encrypt_sensitive_data(self, data, classification):
        if classification == 'HIGH':
            return self.strong_encrypt(data)
        elif classification == 'MEDIUM':
            return self.standard_encrypt(data)
        return data  # Low classification doesn't require encryption
    
    def strong_encrypt(self, data):
        # AES-256 encryption for highly sensitive data
        key = self.get_encryption_key()
        cipher = AES.new(key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(data.encode('utf-8'))
        return base64.b64encode(cipher.nonce + tag + ciphertext).decode('utf-8')
```

**Database Security Measures**:
```python
class DatabaseSecurity:
    def __init__(self):
        self.setup_encryption_at_rest()
        self.configure_secure_connections()
    
    def setup_encryption_at_rest(self):
        # SQLite encryption configuration
        database_config = {
            'SQLALCHEMY_DATABASE_URI': f'sqlite+pysqlcipher://:{db_password}@/{db_path}',
            'SQLALCHEMY_ENGINE_OPTIONS': {
                'connect_args': {'check_same_thread': False},
                'pool_pre_ping': True
            }
        }
    
    def create_secure_backup(self, backup_path):
        # Encrypted database backup
        with open(self.db_path, 'rb') as source:
            encrypted_backup = self.encrypt_file(source.read())
            with open(backup_path, 'wb') as backup:
                backup.write(encrypted_backup)
```

### 7.3.2 Input Sanitization

**Comprehensive Input Validation**:
```python
from markupsafe import escape
from html_sanitizer import Sanitizer

class InputSanitizer:
    def __init__(self):
        self.html_sanitizer = Sanitizer({
            'tags': {'p', 'br', 'strong', 'em', 'code', 'pre'},
            'attributes': {},
            'empty': {'br'},
            'separate': {'p', 'pre'}
        })
    
    def sanitize_user_input(self, input_data, input_type):
        if input_type == 'text':
            return escape(input_data.strip())
        elif input_type == 'html':
            return self.html_sanitizer.sanitize(input_data)
        elif input_type == 'code':
            return self.sanitize_code_input(input_data)
        return input_data
    
    def sanitize_code_input(self, code):
        # Remove dangerous Python constructs for code execution
        dangerous_patterns = [
            r'import\s+os', r'import\s+sys', r'import\s+subprocess',
            r'exec\s*\(', r'eval\s*\(', r'__import__\s*\(',
            r'open\s*\(', r'file\s*\('
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                raise SecurityError(f"Dangerous code pattern detected: {pattern}")
        
        return code
```

**SQL Injection Prevention**:
```python
# Always use parameterized queries through SQLAlchemy ORM
class SecureDataAccess:
    def get_user_sessions(self, user_id, filters):
        # Safe: Using ORM with parameter binding
        query = Session.query.filter(Session.user_id == user_id)
        
        if filters.get('status'):
            query = query.filter(Session.status.in_(filters['status']))
        
        if filters.get('date_range'):
            query = query.filter(
                Session.created_at.between(
                    filters['date_range']['start'],
                    filters['date_range']['end']
                )
            )
        
        return query.all()
```

### 7.3.3 Output Encoding

**Context-Aware Output Encoding**:
```python
class OutputEncoder:
    def encode_for_html(self, data):
        return escape(str(data))
    
    def encode_for_javascript(self, data):
        return json.dumps(data).replace('<', '\\u003c').replace('>', '\\u003e')
    
    def encode_for_css(self, data):
        # CSS context encoding
        return re.sub(r'[<>"\'&\\]', lambda m: f'\\{ord(m.group(0)):06x}', str(data))
    
    def encode_for_url(self, data):
        return urllib.parse.quote(str(data), safe='')
```

## 7.4 Secure Coding Practices

### 7.4.1 Cross-Site Request Forgery (CSRF) Protection

**CSRF Token Implementation**:
```python
from flask_wtf.csrf import CSRFProtect

class CSRFManager:
    def __init__(self, app):
        self.csrf = CSRFProtect(app)
        app.config['SECRET_KEY'] = self.get_secret_key()
    
    def generate_csrf_token(self):
        return secrets.token_urlsafe(32)
    
    def validate_csrf_token(self, token):
        expected_token = session.get('csrf_token')
        return expected_token and secrets.compare_digest(token, expected_token)

# Template usage
# {{ csrf_token() }} in forms
# Automatic validation for POST requests
```

### 7.4.2 Cross-Site Scripting (XSS) Prevention

**Content Security Policy (CSP)**:
```python
class SecurityHeaders:
    def add_security_headers(self, response):
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response
```

### 7.4.3 File Upload Security

**Secure File Handling**:
```python
class FileUploadSecurity:
    ALLOWED_EXTENSIONS = {'html', 'json', 'txt'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    def validate_upload(self, file):
        # Check file extension
        if not self.allowed_file(file.filename):
            raise SecurityError("File type not allowed")
        
        # Check file size
        if len(file.read()) > self.MAX_FILE_SIZE:
            raise SecurityError("File too large")
        file.seek(0)  # Reset file pointer
        
        # Scan for malicious content
        if self.contains_malicious_content(file):
            raise SecurityError("Malicious content detected")
        
        return True
    
    def contains_malicious_content(self, file):
        content = file.read().decode('utf-8', errors='ignore')
        file.seek(0)
        
        malicious_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'data:text/html'
        ]
        
        for pattern in malicious_patterns:
            if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
                return True
        return False
```

## 7.5 Security Testing Approach

### 7.5.1 Automated Security Testing

**Security Test Suite**:
```python
class SecurityTestSuite:
    def test_authentication_security(self):
        # Test password hashing
        assert self.test_password_hashing()
        
        # Test session security
        assert self.test_session_management()
        
        # Test failed login handling
        assert self.test_failed_login_lockout()
    
    def test_input_validation(self):
        # Test SQL injection prevention
        assert self.test_sql_injection_prevention()
        
        # Test XSS prevention
        assert self.test_xss_prevention()
        
        # Test CSRF protection
        assert self.test_csrf_protection()
    
    def test_authorization(self):
        # Test role-based access control
        assert self.test_rbac_enforcement()
        
        # Test resource-level permissions
        assert self.test_resource_permissions()
```

### 7.5.2 Security Monitoring

**Real-time Security Monitoring**:
```python
class SecurityMonitor:
    def __init__(self):
        self.threat_patterns = self.load_threat_patterns()
        self.alert_thresholds = self.load_alert_thresholds()
    
    def monitor_request(self, request):
        # Check for suspicious patterns
        if self.detect_attack_patterns(request):
            self.trigger_security_alert('attack_pattern_detected', request)
        
        # Monitor request rate
        if self.detect_rate_limiting_violation(request):
            self.trigger_security_alert('rate_limit_exceeded', request)
    
    def trigger_security_alert(self, alert_type, context):
        alert = {
            'type': alert_type,
            'timestamp': datetime.utcnow(),
            'source_ip': context.remote_addr,
            'user_agent': context.headers.get('User-Agent'),
            'request_data': self.sanitize_for_logging(context.get_json())
        }
        
        # Log security event
        security_logger.warning(f"Security Alert: {alert_type}", extra=alert)
        
        # Implement response (rate limiting, IP blocking, etc.)
        self.implement_security_response(alert_type, context)
```

This comprehensive security architecture ensures that the PCEP Certification Exam Accelerator maintains robust protection against common web application vulnerabilities while preserving usability and performance for legitimate users.

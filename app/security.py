"""
Security configuration and middleware for Flask application
"""

from flask import request, g, abort, jsonify
import logging
import re
import time
from functools import wraps
from werkzeug.exceptions import BadRequest

logger = logging.getLogger(__name__)
security_logger = logging.getLogger('SECURITY')

# Security patterns for detection
SUSPICIOUS_PATTERNS = [
    # SQL Injection patterns
    r'(\bunion\b.*\bselect\b)',
    r'(\bselect\b.*\bfrom\b)',
    r'(\binsert\b.*\binto\b)',
    r'(\bupdate\b.*\bset\b)',
    r'(\bdelete\b.*\bfrom\b)',
    r'(\bdrop\b.*\btable\b)',
    r'(\balter\b.*\btable\b)',
    r'(\bexec\b.*\()',
    r'(\bexecute\b.*\()',
    r'(\bsp_\w+)',
    r'(\bxp_\w+)',
    r'(\'.*\bor\b.*\')',
    r'(\".*\bor\b.*\")',
    r'(\b1\s*=\s*1\b)',
    r'(\b1\s*=\s*\'1\')',
    r'(\'\s*or\s*\'1\'\s*=\s*\'1)',
    r'(\"\s*or\s*\"1\"\s*=\s*\"1)',

    # XSS patterns
    r'(<script[^>]*>)',
    r'(</script>)',
    r'(<iframe[^>]*>)',
    r'(<object[^>]*>)',
    r'(<embed[^>]*>)',
    r'(<form[^>]*>)',
    r'(javascript:)',
    r'(vbscript:)',
    r'(onload\s*=)',
    r'(onerror\s*=)',
    r'(onclick\s*=)',
    r'(onmouseover\s*=)',
    r'(onfocus\s*=)',
    r'(onblur\s*=)',
    r'(onchange\s*=)',
    r'(onsubmit\s*=)',

    # Path traversal patterns
    r'(\.\.\/)',
    r'(\.\.\\)',
    r'(%2e%2e%2f)',
    r'(%2e%2e%5c)',
    r'(\/etc\/passwd)',
    r'(\/etc\/shadow)',
    r'(\/windows\/system32)',
    r'(c:\\windows\\system32)',

    # Command injection patterns
    r'(\|\s*\w+)',
    r'(;\s*\w+)',
    r'(&\s*\w+)',
    r'(`\w+`)',
    r'(\$\(\w+\))',
    r'(nc\s+-)',
    r'(netcat\s+-)',
    r'(wget\s+)',
    r'(curl\s+)',
    r'(chmod\s+)',
    r'(chown\s+)',

    # File inclusion patterns
    r'(php://)',
    r'(file://)',
    r'(ftp://)',
    r'(data://)',
    r'(expect://)',
    r'(zip://)',
]

# Compile patterns for better performance
COMPILED_PATTERNS = [re.compile(pattern, re.IGNORECASE) for pattern in SUSPICIOUS_PATTERNS]

# Rate limiting storage (in production, use Redis or database)
REQUEST_COUNTS = {}
BLOCKED_IPS = set()

# Security configuration
MAX_REQUESTS_PER_MINUTE = 60
MAX_REQUESTS_PER_HOUR = 1000
BLOCK_DURATION = 3600  # 1 hour in seconds
MAX_PARAM_LENGTH = 1000
MAX_FILENAME_LENGTH = 255
ALLOWED_FILE_EXTENSIONS = {'.xlsx', '.xls'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

def validate_input(value, param_name="parameter"):
    """Validate input for security threats"""
    if not value:
        return True

    value_str = str(value)

    # Get client IP safely
    try:
        client_ip = request.remote_addr if request else 'unknown'
    except RuntimeError:
        client_ip = 'unknown'

    # Check length
    if len(value_str) > MAX_PARAM_LENGTH:
        security_logger.warning(f"Parameter too long: {param_name} length={len(value_str)} from {client_ip}")
        return False

    # Check for suspicious patterns
    for pattern in COMPILED_PATTERNS:
        if pattern.search(value_str):
            security_logger.error(f"Suspicious pattern detected in {param_name}: {value_str[:100]} from {client_ip}")
            return False

    return True

def validate_filename(filename):
    """Validate uploaded filename"""
    if not filename:
        return False

    # Check length
    if len(filename) > MAX_FILENAME_LENGTH:
        return False

    # Check extension
    if not any(filename.lower().endswith(ext) for ext in ALLOWED_FILE_EXTENSIONS):
        return False

    # Check for path traversal
    if '..' in filename or '/' in filename or '\\' in filename:
        return False

    # Check for suspicious characters
    suspicious_chars = ['<', '>', '|', ':', '*', '?', '"']
    if any(char in filename for char in suspicious_chars):
        return False

    return True

def check_rate_limit(client_ip):
    """Check if client IP is within rate limits"""
    current_time = time.time()

    # Clean old entries
    for ip in list(REQUEST_COUNTS.keys()):
        REQUEST_COUNTS[ip] = [timestamp for timestamp in REQUEST_COUNTS[ip] if current_time - timestamp < 3600]
        if not REQUEST_COUNTS[ip]:
            del REQUEST_COUNTS[ip]

    # Check if IP is blocked
    if client_ip in BLOCKED_IPS:
        return False

    # Initialize or update request count
    if client_ip not in REQUEST_COUNTS:
        REQUEST_COUNTS[client_ip] = []

    REQUEST_COUNTS[client_ip].append(current_time)

    # Check rate limits
    recent_requests = [t for t in REQUEST_COUNTS[client_ip] if current_time - t < 60]  # Last minute
    hourly_requests = REQUEST_COUNTS[client_ip]  # Last hour

    if len(recent_requests) > MAX_REQUESTS_PER_MINUTE:
        security_logger.warning(f"Rate limit exceeded (per minute): {client_ip}")
        BLOCKED_IPS.add(client_ip)
        return False

    if len(hourly_requests) > MAX_REQUESTS_PER_HOUR:
        security_logger.warning(f"Rate limit exceeded (per hour): {client_ip}")
        BLOCKED_IPS.add(client_ip)
        return False

    return True

def security_required(f):
    """Decorator for routes that require security validation"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr

        # Skip validation for HEAD requests (used for health checks)
        if request.method == 'HEAD':
            return f(*args, **kwargs)

        # Rate limiting
        if not check_rate_limit(client_ip):
            security_logger.error(f"Request blocked due to rate limiting: {client_ip}")
            abort(429)  # Too Many Requests

        # Validate all form parameters
        for param_name, param_value in request.form.items():
            if not validate_input(param_value, param_name):
                security_logger.error(f"Invalid input detected: {param_name} from {client_ip}")
                abort(400)  # Bad Request

        # Validate all query parameters
        for param_name, param_value in request.args.items():
            if not validate_input(param_value, param_name):
                security_logger.error(f"Invalid query parameter: {param_name} from {client_ip}")
                abort(400)  # Bad Request

        # Validate uploaded files
        for file_key in request.files:
            file = request.files[file_key]
            if file and file.filename:
                if not validate_filename(file.filename):
                    security_logger.error(f"Invalid filename: {file.filename} from {client_ip}")
                    abort(400)  # Bad Request

        return f(*args, **kwargs)
    return decorated_function

def add_security_headers(response):
    """Add comprehensive security headers to response"""
    # Basic security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

    # Cache control
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    # HSTS (HTTP Strict Transport Security) - uncomment for HTTPS
    # response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

    # Content Security Policy (strict)
    csp = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "font-src 'self' https://cdn.jsdelivr.net; "
        "img-src 'self' data:; "
        "connect-src 'self'; "
        "form-action 'self'; "
        "frame-ancestors 'none'; "
        "object-src 'none'; "
        "base-uri 'self'"
    )
    response.headers['Content-Security-Policy'] = csp

    # Additional security headers
    response.headers['X-Permitted-Cross-Domain-Policies'] = 'none'
    response.headers['Cross-Origin-Embedder-Policy'] = 'require-corp'
    response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
    response.headers['Cross-Origin-Resource-Policy'] = 'same-origin'

    # Remove server information
    response.headers.pop('Server', None)

    return response

def init_security(app):
    """Initialize comprehensive security for Flask app"""

    # Ensure Flask only binds to localhost
    if hasattr(app, 'run'):
        original_run = app.run
        def secure_run(*args, **kwargs):
            # Force localhost binding
            kwargs['host'] = '127.0.0.1'
            if 'port' not in kwargs:
                kwargs['port'] = 8080
            return original_run(*args, **kwargs)
        app.run = secure_run

    @app.after_request
    def after_request(response):
        """Add security headers to all responses"""
        return add_security_headers(response)

    @app.before_request
    def before_request():
        """Comprehensive security checks before each request"""
        client_ip = request.remote_addr

        # Block requests from blocked IPs
        if client_ip in BLOCKED_IPS:
            security_logger.error(f"Blocked IP attempted access: {client_ip}")
            abort(403)

        # Validate request method
        if request.method not in ['GET', 'POST', 'HEAD', 'OPTIONS']:
            security_logger.warning(f"Unusual HTTP method: {request.method} from {client_ip}")
            abort(405)

        # Check request size
        if request.content_length and request.content_length > MAX_FILE_SIZE:
            security_logger.warning(f"Request too large: {request.content_length} bytes from {client_ip}")
            abort(413)

        # Log request for security monitoring
        if request.endpoint and not request.endpoint.startswith('static'):
            logger.info(f"Request: {request.method} {request.path} from {client_ip}")

        # Validate User-Agent
        user_agent = request.headers.get('User-Agent', '')
        if not user_agent and request.endpoint and not request.endpoint.startswith('static'):
            security_logger.warning(f"Request without User-Agent from {client_ip}")

        # Check for suspicious User-Agent patterns
        suspicious_ua_patterns = ['sqlmap', 'nikto', 'nmap', 'masscan', 'nessus', 'openvas']
        if any(pattern in user_agent.lower() for pattern in suspicious_ua_patterns):
            security_logger.error(f"Suspicious User-Agent: {user_agent} from {client_ip}")
            BLOCKED_IPS.add(client_ip)
            abort(403)

        # Validate Host header
        host_header = request.headers.get('Host', '')
        allowed_hosts = ['localhost:8080', '127.0.0.1:8080', 'localhost', '127.0.0.1']
        if host_header and host_header not in allowed_hosts:
            security_logger.error(f"Invalid Host header: {host_header} from {client_ip}")
            abort(400)

        # Store request start time for performance monitoring
        g.start_time = time.time()

    @app.errorhandler(400)
    def bad_request(error):
        """Handle bad requests securely"""
        security_logger.warning(f"Bad request from {request.remote_addr}: {error}")
        return jsonify({'error': 'Bad request'}), 400

    @app.errorhandler(403)
    def forbidden(error):
        """Handle forbidden requests"""
        security_logger.warning(f"Forbidden request from {request.remote_addr}: {error}")
        return jsonify({'error': 'Forbidden'}), 403

    @app.errorhandler(404)
    def not_found(error):
        """Handle not found requests"""
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle method not allowed"""
        security_logger.warning(f"Method not allowed from {request.remote_addr}: {error}")
        return jsonify({'error': 'Method not allowed'}), 405

    @app.errorhandler(413)
    def request_entity_too_large(error):
        """Handle request too large"""
        security_logger.warning(f"Request too large from {request.remote_addr}: {error}")
        return jsonify({'error': 'Request too large'}), 413

    @app.errorhandler(429)
    def too_many_requests(error):
        """Handle rate limiting"""
        security_logger.warning(f"Rate limit exceeded from {request.remote_addr}: {error}")
        return jsonify({'error': 'Too many requests'}), 429

    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle internal server errors securely"""
        security_logger.error(f"Internal server error from {request.remote_addr}: {error}")
        return jsonify({'error': 'Internal server error'}), 500

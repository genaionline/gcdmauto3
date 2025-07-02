"""
Security Audit Service - Python equivalent of Java SecurityAuditService
"""

import logging
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from flask import Request

# Create security logger
security_logger = logging.getLogger('SECURITY')

class SecurityAuditService:
    """Security auditing service"""
    
    def log_security_event(self, event_type: str, user_id: str, details: str, request_obj: Optional['Request'] = None):
        """Log security events for monitoring and auditing"""
        client_ip = self._get_client_ip_address(request_obj)
        user_agent = request_obj.headers.get('User-Agent', '') if request_obj else ''
        
        security_logger.warning(
            f"SECURITY_EVENT: {event_type} | User: {user_id} | IP: {client_ip} | "
            f"UserAgent: {user_agent} | Details: {details} | Time: {datetime.now()}"
        )
    
    def log_file_upload(self, user_id: str, file_name: str, file_size: int, market: str, request_obj: Optional['Request'] = None):
        """Log file upload events"""
        client_ip = self._get_client_ip_address(request_obj)

        security_logger.info(
            f"FILE_UPLOAD: User: {user_id} | File: {file_name} | Size: {file_size} bytes | "
            f"Market: {market} | IP: {client_ip} | Time: {datetime.now()}"
        )

    def log_data_access(self, user_id: str, operation: str, filters: str, request_obj: Optional['Request'] = None):
        """Log data access events"""
        client_ip = self._get_client_ip_address(request_obj)

        security_logger.info(
            f"DATA_ACCESS: User: {user_id} | Operation: {operation} | Filters: {filters} | "
            f"IP: {client_ip} | Time: {datetime.now()}"
        )

    def log_admin_operation(self, user_id: str, operation: str, target: str, request_obj: Optional['Request'] = None):
        """Log admin operations"""
        client_ip = self._get_client_ip_address(request_obj)

        security_logger.warning(
            f"ADMIN_OPERATION: User: {user_id} | Operation: {operation} | Target: {target} | "
            f"IP: {client_ip} | Time: {datetime.now()}"
        )

    def log_suspicious_activity(self, event_type: str, details: str, request_obj: Optional['Request'] = None):
        """Log suspicious activities"""
        client_ip = self._get_client_ip_address(request_obj)
        user_agent = request_obj.headers.get('User-Agent', '') if request_obj else ''

        security_logger.error(
            f"SUSPICIOUS_ACTIVITY: Type: {event_type} | IP: {client_ip} | "
            f"UserAgent: {user_agent} | Details: {details} | Time: {datetime.now()}"
        )

    def _get_client_ip_address(self, request_obj: Optional['Request'] = None) -> str:
        """Get client IP address from request"""
        if not request_obj:
            return 'unknown'
        
        # Check for forwarded IP first (in case of proxy/load balancer)
        forwarded_for = request_obj.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        # Check for real IP header
        real_ip = request_obj.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        # Fall back to remote address
        return request_obj.remote_addr or 'unknown'

    def log_file_download(self, user_id: str, file_name: str, request_obj: Optional['Request'] = None):
        """Log file download events"""
        client_ip = self._get_client_ip_address(request_obj)

        security_logger.info(
            f"FILE_DOWNLOAD: User: {user_id} | File: {file_name} | "
            f"IP: {client_ip} | Time: {datetime.now()}"
        )


# Global instance
security_audit_service = SecurityAuditService()

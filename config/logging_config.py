"""
Logging configuration for AutoGen RetrieveChat system
Author: Jay Guwalani
"""

import logging
import logging.config
import os
from datetime import datetime

def setup_logger(name: str = None) -> logging.Logger:
    """Setup logger with appropriate configuration"""
    
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Get log level from environment
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Logging configuration
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'detailed': {
                'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(funcName)s(): %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'json': {
                'format': '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {
            'console': {
                'level': log_level,
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'detailed',
                'filename': f'{log_dir}/retrievechat.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5
            },
            'error_file': {
                'level': 'ERROR',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'detailed',
                'filename': f'{log_dir}/error.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5
            }
        },
        'loggers': {
            '': {  # Root logger
                'handlers': ['console', 'file', 'error_file'],
                'level': 'DEBUG',
                'propagate': False
            },
            'retrievechat': {
                'handlers': ['console', 'file'],
                'level': 'DEBUG',
                'propagate': False
            },
            'autogen': {
                'handlers': ['file'],
                'level': 'INFO',
                'propagate': False
            },
            'chromadb': {
                'handlers': ['file'],
                'level': 'WARNING',
                'propagate': False
            }
        }
    }
    
    # Apply configuration
    logging.config.dictConfig(config)
    
    # Get logger
    logger = logging.getLogger(name or 'retrievechat')
    
    # Log startup information
    if name is None or name == 'retrievechat':
        logger.info("="*60)
        logger.info("AutoGen RetrieveChat System - Logger Initialized")
        logger.info(f"Log Level: {log_level}")
        logger.info(f"Log Directory: {log_dir}")
        logger.info(f"Timestamp: {datetime.now().isoformat()}")
        logger.info("="*60)
    
    return logger

# Example usage logger for other modules
def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module"""
    return logging.getLogger(f"retrievechat.{name}")

# Performance logging utilities
class PerformanceLogger:
    """Utility for logging performance metrics"""
    
    def __init__(self, logger_name: str = "retrievechat.performance"):
        self.logger = logging.getLogger(logger_name)
    
    def log_timing(self, operation: str, duration: float, **kwargs):
        """Log timing information"""
        extra_info = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        message = f"TIMING: {operation} | Duration: {duration:.3f}s"
        if extra_info:
            message += f" | {extra_info}"
        self.logger.info(message)
    
    def log_metric(self, metric_name: str, value: float, unit: str = "", **kwargs):
        """Log performance metric"""
        extra_info = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        message = f"METRIC: {metric_name} | Value: {value}{unit}"
        if extra_info:
            message += f" | {extra_info}"
        self.logger.info(message)
    
    def log_error_rate(self, operation: str, error_count: int, total_count: int):
        """Log error rate information"""
        error_rate = (error_count / total_count * 100) if total_count > 0 else 0
        self.logger.info(f"ERROR_RATE: {operation} | Errors: {error_count}/{total_count} ({error_rate:.2f}%)")

# Security and audit logging
class SecurityLogger:
    """Utility for security and audit logging"""
    
    def __init__(self, logger_name: str = "retrievechat.security"):
        self.logger = logging.getLogger(logger_name)
    
    def log_access(self, user_id: str, endpoint: str, ip_address: str, success: bool):
        """Log access attempts"""
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"ACCESS: {status} | User: {user_id} | Endpoint: {endpoint} | IP: {ip_address}")
    
    def log_sensitive_operation(self, user_id: str, operation: str, resource: str):
        """Log sensitive operations"""
        self.logger.warning(f"SENSITIVE_OP: {operation} | User: {user_id} | Resource: {resource}")
    
    def log_security_event(self, event_type: str, description: str, severity: str = "INFO"):
        """Log security events"""
        log_method = getattr(self.logger, severity.lower(), self.logger.info)
        log_method(f"SECURITY_EVENT: {event_type} | {description}")

"""
Logging utilities for the TrueCred API.

This module configures logging for the application.
"""
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from flask import Flask, request, g
import uuid
from datetime import datetime


def configure_logging(app: Flask, log_level=logging.INFO):
    """
    Configure logging for the Flask application.
    
    Args:
        app: Flask application instance
        log_level: Logging level (default: INFO)
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Set up root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Clear existing handlers to avoid duplicates
    if logger.handlers:
        logger.handlers.clear()
    
    # Create formatters
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(log_level)
    logger.addHandler(console_handler)
    
    # File handler for general logs
    general_handler = RotatingFileHandler(
        os.path.join(log_dir, 'truecred.log'),
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    general_handler.setFormatter(file_formatter)
    general_handler.setLevel(log_level)
    logger.addHandler(general_handler)
    
    # File handler for error logs
    error_handler = RotatingFileHandler(
        os.path.join(log_dir, 'error.log'),
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    error_handler.setFormatter(file_formatter)
    error_handler.setLevel(logging.ERROR)
    logger.addHandler(error_handler)
    
    # Register before request handler to generate request ID
    @app.before_request
    def before_request():
        g.request_id = str(uuid.uuid4())
        g.request_start_time = datetime.utcnow()
    
    # Register after request handler to log request details
    @app.after_request
    def after_request(response):
        # Skip logging for certain paths (e.g., health checks)
        if request.path == '/api/health/check':
            return response
        
        # Calculate request duration
        duration = None
        if hasattr(g, 'request_start_time'):
            duration = (datetime.utcnow() - g.request_start_time).total_seconds() * 1000
        
        # Log request details
        app.logger.info(
            "%s %s %s %s %s %s",
            request.method,
            request.path,
            response.status_code,
            duration,
            request.remote_addr,
            g.get('request_id', 'no-request-id')
        )
        
        # Add request ID to response headers
        response.headers['X-Request-ID'] = g.get('request_id', 'no-request-id')
        
        return response
    
    return logger


def get_logger(name):
    """
    Get a logger with the given name.
    
    Args:
        name: Logger name
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

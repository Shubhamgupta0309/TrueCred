"""
Simplified logging utilities for the TrueCred API.
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
    
    # Set up basic logging configuration
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # Console handler
            logging.StreamHandler(sys.stdout),
            
            # File handler for general logs
            RotatingFileHandler(
                os.path.join(log_dir, 'truecred.log'),
                maxBytes=10485760,  # 10MB
                backupCount=5
            ),
            
            # File handler for error logs
            RotatingFileHandler(
                os.path.join(log_dir, 'error.log'),
                maxBytes=10485760,  # 10MB
                backupCount=5
            )
        ]
    )
    
    # Register before request handler
    @app.before_request
    def before_request():
        g.request_id = str(uuid.uuid4())
        g.request_start_time = datetime.utcnow()
    
    # Register after request handler
    @app.after_request
    def after_request(response):
        # Calculate request duration
        duration = None
        if hasattr(g, 'request_start_time'):
            duration = (datetime.utcnow() - g.request_start_time).total_seconds() * 1000
        
        # Log request details
        app.logger.info(
            "%s %s %s %.2fms %s",
            request.method,
            request.path,
            response.status_code,
            duration if duration else 0,
            request.remote_addr
        )
        
        return response
    
    # Return the configured logger
    return logging.getLogger()


def get_logger(name):
    """
    Get a logger with the given name.
    
    Args:
        name: Logger name
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

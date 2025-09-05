"""
Health check routes for the TrueCred API.
"""
from flask import Blueprint, jsonify, current_app
from utils.health import check_environment
from utils.api_response import success_response, error_response
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Create blueprint
health_bp = Blueprint('health', __name__)

@health_bp.route('/', methods=['GET'])
def health_index():
    """
    Basic health check endpoint.
    """
    return success_response(
        data={
            'status': 'healthy',
            'api_version': current_app.config.get('API_VERSION', '1.0.0'),
            'environment': current_app.config.get('ENV', 'development')
        },
        message='TrueCred API is healthy'
    )

@health_bp.route('/check', methods=['GET'])
def health_check():
    """
    Detailed health check endpoint.
    """
    try:
        health_info, db_connected = check_environment()
        
        # Determine overall status
        status = 'healthy' if db_connected else 'degraded'
        status_code = 200 if db_connected else 207  # 207 Multi-Status
        
        return success_response(
            data={
                'status': status,
                'checks': health_info
            },
            message='Health check completed',
            status_code=status_code
        )
    except Exception as e:
        logger.error(f"Error during health check: {str(e)}")
        return error_response(
            message="Health check failed",
            status_code=500,
            error_code="health_check_error"
        )

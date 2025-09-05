"""
Health check routes for the TrueCred API.
"""
from flask import Blueprint, jsonify, current_app
from utils.health import check_environment

# Create blueprint
health_bp = Blueprint('health', __name__)

@health_bp.route('/', methods=['GET'])
def health_check():
    """
    Get system health status.
    """
    health_info = check_environment()
    
    # Determine overall status
    status = 'healthy'
    if not health_info.get('database_connection', False):
        status = 'unhealthy'
    
    return jsonify({
        'status': status,
        'environment': health_info
    })

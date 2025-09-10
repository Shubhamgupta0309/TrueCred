"""
API blueprint for the TrueCred API.

This module defines the main API blueprint and route registration.
"""
from flask import Blueprint, jsonify, current_app
from utils.api_response import success_response
import logging

# Set up logging
logger = logging.getLogger(__name__)

# API blueprint
api_bp = Blueprint('api', __name__)

@api_bp.route('/')
def index():
    """API index route."""
    return success_response(
        data={
            'name': 'TrueCred API',
            'version': current_app.config.get('API_VERSION', '1.0.0'),
            'environment': current_app.config.get('ENV', 'development'),
            'documentation': '/api/docs'
        },
        message='TrueCred API is running'
    )

@api_bp.route('/status')
def status():
    """API status route."""
    return success_response(
        data={
            'status': 'operational',
            'services': {
                'database': 'connected',
                'authentication': 'operational'
            },
            'version': current_app.config.get('API_VERSION', '1.0.0')
        },
        message='All systems operational'
    )

@api_bp.route('/docs')
def docs():
    """API documentation route."""
    from routes.api_docs import API_ENDPOINTS
    
    return success_response(
        data={
            'api_name': 'TrueCred API',
            'version': current_app.config.get('API_VERSION', '1.0.0'),
            'base_url': '/api',
            'endpoints': API_ENDPOINTS
        },
        message='API documentation'
    )

def register_blueprints(app):
    """
    Register all blueprints with the Flask app.
    
    Args:
        app: Flask application instance
    """
    # Import blueprints
    from routes.auth import auth_bp
    from routes.credentials import credentials_bp
    from routes.experiences import experiences_bp
    from routes.health import health_bp
    from routes.search import search_bp
    from routes.verification import verification_bp
    from routes.blockchain import blockchain_bp
    from routes.ipfs import ipfs_bp
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(credentials_bp, url_prefix='/api/credentials')
    app.register_blueprint(experiences_bp, url_prefix='/api/experiences')
    app.register_blueprint(search_bp, url_prefix='/api/search')
    app.register_blueprint(health_bp, url_prefix='/api/health')
    app.register_blueprint(verification_bp)
    app.register_blueprint(blockchain_bp)
    app.register_blueprint(ipfs_bp)
    
    # Register development-only blueprints if in development mode
    if app.config.get('DEBUG', False):
        try:
            from routes.dev_endpoints import dev_bp
            app.register_blueprint(dev_bp, url_prefix='/api/dev')
            logger.info("Development endpoints registered")
        except ImportError:
            logger.warning("Development endpoints not found, skipping registration")
    
    logger.info("All blueprints registered successfully")

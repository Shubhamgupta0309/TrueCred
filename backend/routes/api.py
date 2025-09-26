"""
API blueprint for the TrueCred API.

This module defines the main API blueprint and route registration.
"""
from flask import Blueprint, jsonify, current_app, request
from utils.api_response import success_response
from models.demo import DemoDocument
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

@api_bp.route('/demo/store', methods=['POST'])
def store_demo():
    """Store a new document in the demo_collection."""
    try:
        data = request.get_json()
        if not data or 'name' not in data or 'value' not in data:
            return jsonify({'error': 'Missing name or value'}), 400
        
        doc = DemoDocument(name=data['name'], value=data['value'])
        doc.save()
        
        return success_response(data={'id': str(doc.id)}, message='Document stored successfully')
    except Exception as e:
        logger.error(f"Error storing demo document: {e}")
        return jsonify({'error': 'Failed to store document'}), 500

@api_bp.route('/demo/fetch', methods=['GET'])
def fetch_demo():
    """Fetch all documents from the demo_collection."""
    try:
        docs = DemoDocument.objects()
        data = [{'id': str(doc.id), 'name': doc.name, 'value': doc.value} for doc in docs]
        
        return success_response(data=data, message='Documents fetched successfully')
    except Exception as e:
        logger.error(f"Error fetching demo documents: {e}")
        return jsonify({'error': 'Failed to fetch documents'}), 500

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
    from routes.experiences_company import company_exp_bp
    from routes.company import company_bp
    from routes.health import health_bp
    from routes.search import search_bp
    from routes.verification import verification_bp
    # from routes.blockchain import blockchain_bp
    from routes.ipfs import ipfs_bp
    from routes.organizations import org_bp
    from routes.organization_student import org_student_bp
    from routes.college import college_bp
    from routes.user import user_bp
    from routes.notifications import notifications_bp
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(credentials_bp, url_prefix='/api/credentials')
    app.register_blueprint(experiences_bp, url_prefix='/api/experiences')
    app.register_blueprint(company_exp_bp)  # Company experience endpoints
    app.register_blueprint(company_bp)  # Company profile endpoints
    app.register_blueprint(search_bp, url_prefix='/api/search')
    app.register_blueprint(health_bp, url_prefix='/api/health')
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
    # Blockchain routes removed - not needed for basic functionality
    app.register_blueprint(ipfs_bp)
    app.register_blueprint(org_bp)
    app.register_blueprint(org_student_bp)
    app.register_blueprint(college_bp)
    app.register_blueprint(user_bp)
    
    # Register development-only blueprints if in development mode
    if app.config.get('DEBUG', False):
        try:
            from routes.dev_endpoints import dev_bp
            app.register_blueprint(dev_bp, url_prefix='/api/dev')
            logger.info("Development endpoints registered")
        except ImportError:
            logger.warning("Development endpoints not found, skipping registration")
    
    logger.info("All blueprints registered successfully")

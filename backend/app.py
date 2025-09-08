"""
TrueCred Backend Application

This is the main application entry point for the TrueCred backend.
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import get_config
from utils.database import init_db
from utils.simple_logging import configure_logging
from utils.error_handlers import register_error_handlers
from utils.api_response import error_response
from datetime import datetime
import logging
import os

# JWT manager
jwt = JWTManager()

# Simple in-memory token blacklist
# In a production environment, you would use Redis or another database
# to store blacklisted tokens
token_blacklist = set()

def create_app(config_name='default'):
    """
    Application factory function to create and configure the Flask app.
    
    Args:
        config_name: The configuration to use (default, development, testing, production)
        
    Returns:
        The configured Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Set up logging
    configure_logging(app, log_level=app.config.get('LOG_LEVEL', logging.INFO))
    logger = logging.getLogger(__name__)
    
    # Initialize extensions with custom CORS settings
    from middleware.cors import configure_cors
    configure_cors(app)
    
    # Initialize database
    logger.info("Initializing database connection...")
    init_db(app)
    logger.info("Database connection initialized successfully")
    
    # Set current time (useful for tests)
    app.config['CURRENT_TIME'] = datetime.utcnow()
    
    # Initialize JWT
    jwt.init_app(app)
    
    # JWT configuration
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blacklist(jwt_header, jwt_payload):
        """Check if a token is in the blacklist."""
        jti = jwt_payload["jti"]
        return jti in token_blacklist

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        """Handler for expired tokens."""
        return error_response(
            message="The token has expired",
            status_code=401,
            error_code="token_expired"
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        """Handler for invalid tokens."""
        return error_response(
            message="Signature verification failed",
            status_code=401,
            error_code="invalid_token"
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        """Handler for missing tokens."""
        return error_response(
            message="Authorization required",
            status_code=401,
            error_code="authorization_required"
        )

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        """Handler for non-fresh tokens."""
        return error_response(
            message="Fresh token required",
            status_code=401,
            error_code="fresh_token_required"
        )

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        """Handler for revoked tokens."""
        return error_response(
            message="Token has been revoked",
            status_code=401,
            error_code="token_revoked"
        )
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    from routes.api import register_blueprints
    register_blueprints(app)
    
    # Root route
    @app.route('/')
    def index():
        return jsonify({
            'name': 'TrueCred API',
            'version': app.config.get('API_VERSION', '1.0.0'),
            'status': 'Running'
        })
    
    logger.info(f"TrueCred API initialized in {app.config.get('ENV', 'development')} mode")
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        host=os.getenv('FLASK_HOST', '0.0.0.0'),
        port=int(os.getenv('FLASK_PORT', 5000)),
        debug=app.config.get('DEBUG', False)
    )

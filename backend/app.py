"""
TrueCred Backend Application

This is the main application entry point for the TrueCred backend.
"""
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import get_config
from utils.database import init_db, get_db

# JWT manager
jwt = JWTManager()

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
    app.config.from_object(get_config())
    
    # Initialize extensions
    CORS(app)
    init_db(app)
    jwt.init_app(app)
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.credentials import credentials_bp
    from routes.experiences import experiences_bp
    from routes.health import health_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(credentials_bp, url_prefix='/api/credentials')
    app.register_blueprint(experiences_bp, url_prefix='/api/experiences')
    app.register_blueprint(health_bp, url_prefix='/api/health')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({'error': 'Server error'}), 500
    
    # Root route
    @app.route('/')
    def index():
        return jsonify({
            'name': 'TrueCred API',
            'version': '1.0.0',
            'status': 'Running'
        })
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

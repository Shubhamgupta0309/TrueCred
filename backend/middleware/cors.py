"""
CORS configuration middleware for TrueCred
"""
from flask_cors import CORS

def configure_cors(app):
    """
    Configure CORS for the application.
    
    Args:
        app: Flask application instance
    """
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "http://localhost:3000",  # React default port
                "http://localhost:5173",  # Vite default port
                "http://127.0.0.1:3000",
                "http://127.0.0.1:5173",
                # Add production URLs as needed
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"]
        }
    })
    
    return app

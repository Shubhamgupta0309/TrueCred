"""
TrueCred Backend Application

This is the main application entry point for the TrueCred backend.
"""
import sys
import os

# Add parent directory to path for relative imports when run directly
if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
import subprocess
import atexit
import time

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
    # Disable strict slashes so Flask won't redirect requests that differ only by trailing slash.
    # Redirect responses break CORS preflight (browsers disallow redirects for OPTIONS requests).
    app.url_map.strict_slashes = False
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Set up logging
    configure_logging(app, log_level=app.config.get('LOG_LEVEL', logging.INFO))
    logger = logging.getLogger(__name__)
    
    # Initialize extensions with custom CORS settings
    from middleware.cors import configure_cors
    configure_cors(app)
    
    # Set up request/response logging middleware
    from middleware.logging import setup_logging_middleware
    setup_logging_middleware(app)
    
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

    # Optionally auto-start a local IPFS daemon in development for convenience.
    # WARNING: this is intended for local development only. Do NOT enable in production.
    try:
        start_daemon = str(os.getenv('START_IPFS_DAEMON', 'false')).lower() in ('1', 'true', 'yes')
        # Auto-start when START_IPFS_DAEMON is truthy (developer opt-in). Do not require Flask ENV to be 'development'.
        if start_daemon:
            # Attempt to start ipfs daemon if HTTP API is not reachable.
            from services.ipfs_service import IPFSService
            ipfs_api = os.getenv('IPFS_API_URL', 'http://127.0.0.1:5001')
            # Support two env names for the ipfs binary path
            ipfs_cli = os.getenv('IPFS_CLI_PATH') or os.getenv('IPFS_BINARY_PATH') or 'ipfs'

            # Ensure instance path exists for logs/pid (fallback)
            try:
                os.makedirs(app.instance_path, exist_ok=True)
            except Exception:
                pass

            # Allow overriding log directory
            ipfs_log_dir = os.getenv('IPFS_LOG_DIR', app.instance_path)
            try:
                os.makedirs(ipfs_log_dir, exist_ok=True)
            except Exception:
                pass

            pid_file = os.path.join(ipfs_log_dir, 'ipfs_daemon.pid')
            log_file_path = os.path.join(ipfs_log_dir, 'ipfs_daemon.log')

            def _start_ipfs_daemon():
                try:
                    svc = IPFSService(api_url=ipfs_api)
                    if svc.connect():
                        logger.info('IPFS HTTP API already reachable; skipping auto-start of ipfs daemon.')
                        return None
                except Exception:
                    # proceed to try to start daemon
                    pass

                try:
                    # Start ipfs daemon in background
                    logfile = open(log_file_path, 'a')
                    proc = subprocess.Popen([ipfs_cli, 'daemon'], stdout=logfile, stderr=subprocess.STDOUT, cwd=app.instance_path)
                    # write pid file
                    with open(pid_file, 'w') as f:
                        f.write(str(proc.pid))
                    logger.info(f'Started ipfs daemon (PID: {proc.pid}), logs: {log_file_path}, binary: {ipfs_cli}')

                    # register cleanup
                    def _cleanup():
                        try:
                            if proc.poll() is None:
                                logger.info('Terminating ipfs daemon started by backend')
                                proc.terminate()
                                # give it a moment
                                time.sleep(1)
                                if proc.poll() is None:
                                    proc.kill()
                        except Exception:
                            pass
                        try:
                            if os.path.exists(pid_file):
                                os.remove(pid_file)
                        except Exception:
                            pass

                    atexit.register(_cleanup)
                    return proc
                except FileNotFoundError:
                    logger.warning('ipfs binary not found on PATH; cannot auto-start daemon. Set IPFS_CLI_PATH to the ipfs executable if you want auto-start.')
                except Exception as e:
                    logger.warning(f'Failed to start ipfs daemon automatically: {e}')

            # Try to start daemon but don't block app startup
            try:
                proc = _start_ipfs_daemon()
                if proc:
                    app.config['IPFS_DAEMON_PROCESS'] = proc
            except Exception as e:
                logger.warning(f'Error attempting to auto-start ipfs daemon: {e}')
    except Exception:
        # best-effort convenience; do not fail app startup
        pass
    
    logger.info(f"TrueCred API initialized in {app.config.get('ENV', 'development')} mode")
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        host=os.getenv('FLASK_HOST', '0.0.0.0'),
        port=int(os.getenv('FLASK_PORT', 5000)),
        debug=app.config.get('DEBUG', False)
    )

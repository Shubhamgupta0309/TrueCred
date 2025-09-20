"""
Configuration settings for the TrueCred application.
"""
import os
import logging
from dotenv import load_dotenv
from datetime import timedelta

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration."""
    # Application configuration
    ENV = 'development'
    DEBUG = False
    TESTING = False
    API_VERSION = '1.0.0'
    LOG_LEVEL = logging.INFO
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'default-jwt-secret-key')
    
    # Database
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/truecred')
    
    # JWT Configuration
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    JWT_ERROR_MESSAGE_KEY = 'message'
    
    # IPFS Configuration
    IPFS_API_URL = os.environ.get('IPFS_API_URL', '/ip4/127.0.0.1/tcp/5001')
    
    # Ethereum Configuration
    INFURA_PROJECT_ID = os.environ.get('INFURA_PROJECT_ID')
    ETHEREUM_NETWORK = os.environ.get('ETHEREUM_NETWORK', 'goerli')
    CONTRACT_ADDRESS = os.environ.get('CONTRACT_ADDRESS')
    
    # Email Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@truecred.com')
    
    # Frontend URL for email links
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
    
    # Rate Limiting Configuration
    RATE_LIMITS = {
        'default': {'requests': 100, 'window': 60},     # 100 requests per minute
        'auth': {'requests': 5, 'window': 60},          # 5 auth requests per minute
        'upload': {'requests': 10, 'window': 3600},     # 10 uploads per hour
        'verification': {'requests': 20, 'window': 60}, # 20 verification requests per minute
        'search': {'requests': 30, 'window': 60}        # 30 search requests per minute
    }
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB max file size
    ALLOWED_FILE_TYPES = ['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'txt']
    
    # Security Configuration
    REQUIRE_HTTPS = os.environ.get('REQUIRE_HTTPS', 'False').lower() == 'true'
    ENABLE_CORS = True
    CORS_ORIGINS = [
        'http://localhost:5173',
        'http://127.0.0.1:5173',
        'http://localhost:3000',
        'http://127.0.0.1:3000'
    ]

class DevelopmentConfig(Config):
    """Development configuration."""
    ENV = 'development'
    DEBUG = True
    TESTING = False
    LOG_LEVEL = logging.DEBUG
    
    # For development, we can use a shorter token expiry
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)

class TestingConfig(Config):
    """Testing configuration."""
    ENV = 'testing'
    DEBUG = False
    TESTING = True
    LOG_LEVEL = logging.DEBUG
    
    # Database
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/truecred_test')
    
    # For testing, we can use even shorter token expiry
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(hours=1)

class ProductionConfig(Config):
    """Production configuration."""
    ENV = 'production'
    DEBUG = False
    TESTING = False
    LOG_LEVEL = logging.WARNING
    
    # In production, ensure all secret keys are properly set
    # and consider using more secure settings

# Dictionary for mapping configuration based on environment
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config(config_name='default'):
    """
    Get the configuration based on the environment.
    
    Args:
        config_name: Configuration name (default, development, testing, production)
        
    Returns:
        Configuration class
    """
    if config_name in config:
        return config[config_name]
    
    # Use environment variable if config_name is not provided
    env = os.environ.get('FLASK_ENV', 'default')
    return config.get(env, config['default'])

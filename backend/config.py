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

"""
Configuration settings for the TrueCred application.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'default-jwt-secret-key')
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/truecred')
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    
    # IPFS Configuration
    IPFS_API_URL = os.environ.get('IPFS_API_URL', '/ip4/127.0.0.1/tcp/5001')
    
    # Ethereum Configuration
    INFURA_PROJECT_ID = os.environ.get('INFURA_PROJECT_ID')
    ETHEREUM_NETWORK = os.environ.get('ETHEREUM_NETWORK', 'goerli')
    CONTRACT_ADDRESS = os.environ.get('CONTRACT_ADDRESS')

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = False
    TESTING = True
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/truecred_test')

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    # In production, ensure all secret keys are properly set
    # and consider using more secure settings

# Dictionary for mapping configuration based on environment
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get the configuration based on the environment."""
    env = os.environ.get('FLASK_ENV', 'default')
    return config.get(env, config['default'])

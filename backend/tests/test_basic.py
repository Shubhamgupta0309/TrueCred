"""
Basic tests for the TrueCred API.
"""
import pytest
from app import create_app
from config import TestConfig

@pytest.fixture
def app():
    """
    Create a Flask app for testing.
    """
    app = create_app()
    app.config.from_object(TestConfig)
    return app

@pytest.fixture
def client(app):
    """
    Create a test client.
    """
    return app.test_client()

def test_index(client):
    """
    Test the index route.
    """
    response = client.get('/')
    assert response.status_code == 200
    assert b'TrueCred API' in response.data

def test_health_check(client):
    """
    Test the health check route.
    """
    response = client.get('/api/health')
    assert response.status_code == 200
    assert b'status' in response.data

def test_auth_endpoints_exist(client):
    """
    Test that auth endpoints exist.
    """
    # Register endpoint
    response = client.post('/api/auth/register')
    assert response.status_code != 404
    
    # Login endpoint
    response = client.post('/api/auth/login')
    assert response.status_code != 404
    
    # Profile endpoint should require authentication
    response = client.get('/api/auth/profile')
    assert response.status_code != 404

def test_credentials_endpoints_exist(client):
    """
    Test that credentials endpoints exist.
    """
    # Get credentials endpoint
    response = client.get('/api/credentials/')
    assert response.status_code != 404
    
    # Create credential endpoint
    response = client.post('/api/credentials/')
    assert response.status_code != 404
    
    # Get specific credential endpoint
    response = client.get('/api/credentials/1')
    assert response.status_code != 404

def test_experiences_endpoints_exist(client):
    """
    Test that experiences endpoints exist.
    """
    # Get experiences endpoint
    response = client.get('/api/experiences/')
    assert response.status_code != 404
    
    # Create experience endpoint
    response = client.post('/api/experiences/')
    assert response.status_code != 404
    
    # Get specific experience endpoint
    response = client.get('/api/experiences/1')
    assert response.status_code != 404

"""
Health check utility for the TrueCred application.
"""
import os
import sys
import importlib.util
import platform
from datetime import datetime
import logging

# Set up logging
logger = logging.getLogger(__name__)

def check_database_connection():
    """
    Check if the database connection is working.
    
    Returns:
        Tuple of (is_connected, details)
    """
    try:
        from utils.database import get_db
        db = get_db()
        
        # Try to perform a simple operation
        collection_names = db.db.list_collection_names()
        
        return True, {
            'status': 'connected',
            'collections': collection_names
        }
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        return False, {
            'status': 'error',
            'message': str(e)
        }

def check_environment():
    """
    Check the environment for required dependencies and configurations.
    
    Returns:
        Dictionary with health check results
    """
    start_time = datetime.utcnow()
    
    # Basic system information
    system_info = {
        'system': platform.system(),
        'python_version': sys.version,
        'node': platform.node(),
        'time': datetime.utcnow().isoformat()
    }
    
    # Check dependencies
    dependencies = {
        'flask': True,
        'pymongo': True,
        'mongoengine': True,
        'flask_jwt_extended': True,
        'flask_cors': True,
        'python-dotenv': True
    }
    
    for dep in dependencies.keys():
        module_name = dep.replace('-', '_')
        try:
            spec = importlib.util.find_spec(module_name)
            if spec is not None:
                module = importlib.import_module(module_name)
                version = getattr(module, '__version__', 'Unknown')
                dependencies[dep] = {
                    'installed': True,
                    'version': version
                }
            else:
                dependencies[dep] = {
                    'installed': False,
                    'version': None
                }
        except ImportError:
            dependencies[dep] = {
                'installed': False,
                'version': None
            }
    
    # Check database connection
    db_connected, db_details = check_database_connection()
    
    # Assemble results
    results = {
        'system': system_info,
        'dependencies': dependencies,
        'database': db_details,
        'uptime': str(datetime.utcnow() - start_time)
    }
    
    return results, db_connected

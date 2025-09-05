"""
Health check utility for the TrueCred application.
"""
import os
import sys
import importlib.util
import platform
from flask import current_app

def check_environment():
    """
    Check the environment for required dependencies and configurations.
    
    Returns:
        Dictionary with health check results
    """
    results = {
        'system': platform.system(),
        'python_version': sys.version,
        'dependencies': {},
        'environment_variables': {},
        'database_connection': False,
        'blockchain_connection': False,
        'ipfs_connection': False
    }
    
    # Check dependencies
    dependencies = [
        'flask', 'pymongo', 'flask_jwt_extended', 'web3', 'ipfshttpclient',
        'flask_cors', 'python-dotenv'
    ]
    
    for dep in dependencies:
        try:
            spec = importlib.util.find_spec(dep.replace('-', '_'))
            if spec is not None:
                module = importlib.import_module(dep.replace('-', '_'))
                version = getattr(module, '__version__', 'Unknown')
                results['dependencies'][dep] = {
                    'installed': True,
                    'version': version
                }
            else:
                results['dependencies'][dep] = {
                    'installed': False,
                    'version': None
                }
        except ImportError:
            results['dependencies'][dep] = {
                'installed': False,
                'version': None
            }
    
    # Check environment variables
    env_vars = [
        'FLASK_APP', 'FLASK_ENV', 'MONGO_URI', 'JWT_SECRET_KEY',
        'WEB3_PROVIDER_URI', 'IPFS_HOST', 'IPFS_PORT'
    ]
    
    for var in env_vars:
        results['environment_variables'][var] = os.environ.get(var, 'Not set')
    
    # Check database connection
    try:
        from utils.database import get_db
        mongo = get_db()
        if mongo and mongo.db:
            # Try a simple operation
            collections = mongo.db.list_collection_names()
            results['database_connection'] = True
            results['database_collections'] = collections
    except Exception as e:
        results['database_error'] = str(e)
    
    # Check blockchain connection
    try:
        from utils.blockchain import BlockchainUtil
        web3_uri = os.environ.get('WEB3_PROVIDER_URI', 'http://127.0.0.1:8545')
        blockchain_util = BlockchainUtil(web3_uri)
        results['blockchain_connection'] = blockchain_util.is_connected()
    except Exception as e:
        results['blockchain_error'] = str(e)
    
    # Check IPFS connection
    try:
        from utils.ipfs import IPFSUtil
        ipfs_host = os.environ.get('IPFS_HOST', '127.0.0.1')
        ipfs_port = int(os.environ.get('IPFS_PORT', '5001'))
        ipfs_util = IPFSUtil(ipfs_host, ipfs_port)
        results['ipfs_connection'] = ipfs_util.connect()
    except Exception as e:
        results['ipfs_error'] = str(e)
    
    return results

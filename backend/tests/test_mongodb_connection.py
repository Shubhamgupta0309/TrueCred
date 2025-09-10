"""
Test MongoDB connection for TrueCred project.
"""
import os
import sys
from mongoengine import connect, disconnect
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

def test_mongodb_connection():
    """Test MongoDB connection."""
    mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/truecred')
    print(f"Testing connection to MongoDB with URI: {mongo_uri}")
    
    try:
        # Disconnect any existing connections
        disconnect()
        
        # Connect to MongoDB
        conn = connect(host=mongo_uri)
        
        # Test connection
        result = conn.server_info()
        print("Connection successful!")
        print(f"MongoDB version: {result.get('version')}")
        
        # Check database
        db_names = conn.list_database_names()
        print(f"Available databases: {', '.join(db_names)}")
        
        return True
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return False

if __name__ == "__main__":
    test_mongodb_connection()

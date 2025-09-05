"""
Test script to verify MongoDB Atlas connection.
"""
import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

def test_mongodb_connection():
    """
    Test the connection to MongoDB Atlas.
    """
    print("=== MongoDB Atlas Connection Test ===")
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Get MongoDB URI from environment
    mongo_uri = os.environ.get('MONGO_URI')
    
    if not mongo_uri:
        print("❌ MONGO_URI not found in environment variables.")
        return False
    
    print(f"📝 Using connection string: {mongo_uri.replace('truecred:truecred', 'truecred:****')}")
    
    try:
        # Connect to MongoDB
        client = MongoClient(mongo_uri)
        
        # The ismaster command is cheap and does not require auth
        client.admin.command('ismaster')
        print("✅ Connected to MongoDB Atlas successfully!")
        
        # Get database info
        db_names = client.list_database_names()
        print(f"📊 Available databases: {', '.join(db_names)}")
        
        # Check for the TrueCred database
        if 'truecred' in db_names:
            print("✅ TrueCred database exists.")
            db = client['truecred']
            
            # Check for collections
            collections = db.list_collection_names()
            if collections:
                print(f"📋 Collections in TrueCred database: {', '.join(collections)}")
            else:
                print("ℹ️ No collections found in TrueCred database. This is normal for a new database.")
        else:
            print("ℹ️ TrueCred database not found. It will be created when you first store data.")
        
        # Create a test collection and document
        try:
            db = client['truecred']
            test_collection = db['connection_test']
            
            # Insert a test document
            result = test_collection.insert_one({
                'test': 'connection',
                'status': 'success',
                'message': 'MongoDB Atlas connection is working!'
            })
            
            print(f"✅ Created test document with ID: {result.inserted_id}")
            
            # Clean up - delete the test document
            test_collection.delete_one({'_id': result.inserted_id})
            print("🧹 Cleaned up test document.")
            
        except Exception as e:
            print(f"⚠️ Could perform write operations: {e}")
            return False
        
        return True
    
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB Atlas: {e}")
        
        # Provide some troubleshooting advice
        print("\nTroubleshooting tips:")
        print("1. Check if your IP address is whitelisted in MongoDB Atlas Network Access")
        print("2. Verify your username and password in the connection string")
        print("3. Ensure you have the pymongo[srv] package installed")
        print("4. Check your internet connection")
        
        return False

if __name__ == "__main__":
    if test_mongodb_connection():
        print("\n🎉 Success! Your MongoDB Atlas connection is working properly.")
        print("You can now proceed with the TrueCred backend development.")
    else:
        print("\n❌ Could not connect to MongoDB Atlas. Please fix the issues before continuing.")
        sys.exit(1)

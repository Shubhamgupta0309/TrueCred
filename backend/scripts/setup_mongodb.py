"""
Setup script for MongoDB connection.
"""
import os
import sys
import subprocess
import platform
from dotenv import load_dotenv

def check_mongodb_installed():
    """
    Check if MongoDB is installed locally.
    
    Returns:
        True if MongoDB is installed, False otherwise
    """
    try:
        # Try to run mongod --version
        result = subprocess.run(
            ['mongod', '--version'], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False

def setup_mongodb():
    """
    Guide the user through setting up MongoDB.
    """
    print("\n=== MongoDB Setup ===")
    
    # Check if MongoDB is installed
    if check_mongodb_installed():
        print("✅ MongoDB is installed.")
    else:
        print("❌ MongoDB is not installed.")
        print("\nPlease install MongoDB:")
        
        system = platform.system()
        if system == "Windows":
            print("1. Download the MongoDB Community Server from https://www.mongodb.com/try/download/community")
            print("2. Follow the installation instructions")
        elif system == "Darwin":  # macOS
            print("1. Install using Homebrew: brew tap mongodb/brew && brew install mongodb-community")
        else:  # Linux
            print("1. Follow the instructions at https://docs.mongodb.com/manual/administration/install-on-linux/")
        
        print("\nAfter installation, run this script again.")
        return False
    
    # Check if MONGO_URI is set in .env
    load_dotenv()
    mongo_uri = os.environ.get('MONGO_URI')
    
    if not mongo_uri:
        print("❌ MONGO_URI is not set in the .env file.")
        
        # Suggest a default URI
        default_uri = "mongodb://localhost:27017/truecred"
        
        # Ask the user if they want to use the default URI
        response = input(f"Do you want to use the default URI '{default_uri}'? (y/n): ")
        
        if response.lower() == 'y':
            # Update the .env file
            with open('.env', 'a') as f:
                f.write(f"\nMONGO_URI={default_uri}\n")
            print(f"✅ Added MONGO_URI={default_uri} to .env file.")
        else:
            uri = input("Enter your MongoDB URI: ")
            with open('.env', 'a') as f:
                f.write(f"\nMONGO_URI={uri}\n")
            print(f"✅ Added MONGO_URI={uri} to .env file.")
    else:
        print(f"✅ MONGO_URI is set to {mongo_uri}")
    
    # Verify the connection
    try:
        import pymongo
        client = pymongo.MongoClient(os.environ.get('MONGO_URI', "mongodb://localhost:27017/truecred"))
        # The ismaster command is cheap and does not require auth
        client.admin.command('ismaster')
        print("✅ Successfully connected to MongoDB.")
        return True
    except pymongo.errors.ConnectionFailure:
        print("❌ Failed to connect to MongoDB. Please make sure MongoDB is running.")
        return False
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")
        return False

if __name__ == "__main__":
    print("TrueCred MongoDB Setup Script")
    setup_mongodb()

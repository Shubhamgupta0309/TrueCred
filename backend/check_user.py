"""Script to check if a user exists in the database."""
from pymongo import MongoClient
import sys
import os
from werkzeug.security import generate_password_hash
from bson import ObjectId

def check_and_setup_user(email, password, full_name, role):
    """Check if a user exists and create if not."""
    try:
        # Write to file that we're starting
        with open('user_setup.log', 'w') as f:
            f.write("Starting user setup...\n")
            
        # Connect to MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client.truecred
        
        # Find the user
        user = db.users.find_one({'email': email})
        
        if user:
            with open('user_setup.log', 'a') as f:
                f.write(f"\nUser found:\n")
                f.write(f"Email: {user.get('email')}\n")
                f.write(f"Full Name: {user.get('fullName', user.get('full_name', ''))}\n")
                f.write(f"Role: {user.get('role')}\n")
                f.write(f"Has password: {'Yes' if user.get('password') else 'No'}\n")
            
            # Update password if needed
            if not user.get('password'):
                hashed_password = generate_password_hash(password)
                db.users.update_one(
                    {'_id': user['_id']},
                    {'$set': {'password': hashed_password}}
                )
                with open('user_setup.log', 'a') as f:
                    f.write("Added missing password to user\n")
        else:
            # Create new user
            new_user = {
                '_id': ObjectId(),
                'email': email,
                'password': generate_password_hash(password),
                'fullName': full_name,
                'role': role,
                'is_active': True,
                'is_verified': True
            }
            db.users.insert_one(new_user)
            with open('user_setup.log', 'a') as f:
                f.write(f"\nCreated new user:\n")
                f.write(f"Email: {email}\n")
                f.write(f"Full Name: {full_name}\n")
                f.write(f"Role: {role}\n")
            
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    email = "shubham.gupta300904@gmail.com"
    password = "Shubham@1234"
    full_name = "Shubham Gupta"
    role = "student"
    
    with open('user_setup.log', 'w') as f:
        f.write(f"\nChecking/setting up user: {email}\n")
    check_and_setup_user(email, password, full_name, role)

#!/usr/bin/env python3
"""
Check users in database
"""
import sys
import os

# Add the backend directory to the Python path
backend_path = os.path.dirname(__file__)
sys.path.insert(0, backend_path)

try:
    # Set up environment
    os.environ.setdefault('FLASK_ENV', 'development')

    from models.user import User
    from config import get_config
    from utils.database import init_db
    from flask import Flask

    # Create Flask app for database connection
    app = Flask(__name__)
    config = get_config('development')
    app.config.from_object(config)

    # Initialize database
    with app.app_context():
        init_db(app)

        def check_users():
            print("Checking users in database...")
            print("=" * 50)

            # Check if there are any users
            users = User.objects.all()
            print(f'Total users: {len(users)}')

            if len(users) == 0:
                print("No users found in database!")
                return

            for i, user in enumerate(users, 1):
                print(f'\n--- User {i} ---')
                print(f'ID: {user.id}')
                print(f'Username: {user.username}')
                print(f'Email: {user.email}')
                print(f'Role: {user.role}')
                print(f'First Name: {user.first_name}')
                print(f'Last Name: {user.last_name}')
                print(f'TrueCred ID: {user.truecred_id}')
                print(f'Created: {user.created_at}')

        check_users()

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
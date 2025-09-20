#!/usr/bin/env python3
"""
Check college profiles in database
"""
import sys
import os

# Add the backend directory to the Python path
backend_path = os.path.dirname(__file__)
sys.path.insert(0, backend_path)

try:
    # Set up environment
    os.environ.setdefault('FLASK_ENV', 'development')

    from models.organization_profile import OrganizationProfile
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

        def check_college_profiles():
            print("Checking college profiles in database...")
            print("=" * 50)

            # Check if there are any college profiles
            profiles = OrganizationProfile.objects.all()
            print(f'Total college profiles: {len(profiles)}')

            if len(profiles) == 0:
                print("No college profiles found in database!")
                return

            for i, profile in enumerate(profiles, 1):
                print(f'\n--- College Profile {i} ---')
                print(f'ID: {profile.id}')
                print(f'User ID: {profile.user_id}')
                print(f'Institution Name: {profile.name}')
                print(f'Full Name: {profile.fullName}')
                print(f'Created: {profile.created_at}')

                # Get the associated user
                user = User.objects(id=profile.user_id).first()
                if user:
                    print(f'Associated User: {user.username} ({user.email}) - Role: {user.role}')
                else:
                    print('Associated User: Not found')

        check_college_profiles()

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
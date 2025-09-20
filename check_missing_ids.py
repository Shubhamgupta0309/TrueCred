#!/usr/bin/env python3
"""
Script to check for users without TrueCred IDs and optionally assign them.
"""
import sys
import os

# Add the backend directory to the Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from backend.models.user import User
from backend.services.auth_service import AuthService
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_missing_truecred_ids():
    """Check for users who don't have TrueCred IDs."""
    print("Checking for users without TrueCred IDs...")
    print("=" * 50)

    try:
        # Count total users
        total_users = User.objects.count()
        print(f"Total users in database: {total_users}")

        # Count users with TrueCred IDs
        users_with_ids = User.objects(truecred_id__exists=True).count()
        print(f"Users with TrueCred IDs: {users_with_ids}")

        # Count users without TrueCred IDs
        users_without_ids = User.objects(truecred_id__exists=False).count()
        print(f"Users without TrueCred IDs: {users_without_ids}")

        if users_without_ids > 0:
            print(f"\nFound {users_without_ids} users without TrueCred IDs:")
            users_missing = User.objects(truecred_id__exists=False).only('username', 'email').all()
            for i, user in enumerate(users_missing, 1):
                print(f"  {i}. Username: {user.username}, Email: {user.email}")

            # Ask if user wants to assign IDs
            response = input(f"\nDo you want to assign TrueCred IDs to these {users_without_ids} users? (y/N): ").lower().strip()
            if response == 'y' or response == 'yes':
                print("Assigning TrueCred IDs...")
                success_count, error_count = AuthService.assign_missing_truecred_ids()
                print(f"Assignment completed: {success_count} successful, {error_count} errors")
            else:
                print("Assignment cancelled.")
        else:
            print("\nAll users have TrueCred IDs! ✓")

    except Exception as e:
        print(f"Error checking users: {e}")
        logger.error(f"Error in check_missing_truecred_ids: {e}")

if __name__ == "__main__":
    check_missing_truecred_ids()
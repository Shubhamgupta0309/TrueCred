#!/usr/bin/env python3
"""
Check credential requests in database
"""
import sys
import os

# Add the backend directory to the Python path
backend_path = os.path.dirname(__file__)
sys.path.insert(0, backend_path)

try:
    # Set up environment
    os.environ.setdefault('FLASK_ENV', 'development')

    from models.credential_request import CredentialRequest
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

        def check_requests():
            print("Checking credential requests in database...")
            print("=" * 50)

            # Check if there are any credential requests
            requests = CredentialRequest.objects.all()
            print(f'Total credential requests: {len(requests)}')

            if len(requests) == 0:
                print("No credential requests found in database!")
                print("This explains why the CollegeDashboard shows 'No pending requests'")
                return

            for i, req in enumerate(requests, 1):
                print(f'\n--- Request {i} ---')
                print(f'ID: {req.id}')
                print(f'Title: {req.title}')
                print(f'Status: {req.status}')
                print(f'Issuer: {req.issuer}')
                print(f'Issuer ID: {req.issuer_id}')
                print(f'User ID: {req.user_id}')
                print(f'Created: {req.created_at}')
                print(f'Attachments: {req.attachments}')
                print(f'Attachments count: {len(req.attachments) if req.attachments else 0}')
                
                if req.attachments:
                    for j, att in enumerate(req.attachments, 1):
                        print(f'  Attachment {j}: {att}')

                # Get user info
                user = User.objects(id=req.user_id).first()
                if user:
                    print(f'User: {user.username} ({user.email}) - Role: {user.role}')
                else:
                    print('User: Not found')

                # Get issuer info
                if req.issuer_id:
                    issuer = User.objects(id=req.issuer_id).first()
                    if issuer:
                        print(f'Issuer User: {issuer.username} ({issuer.email}) - Role: {issuer.role}')
                    else:
                        print('Issuer User: Not found')

        check_requests()

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
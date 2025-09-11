#!/usr/bin/env python3
"""
TrueCred Backend Application
A Flask application that provides API endpoints for the TrueCred platform.
"""
import os
import json
import logging
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path

import jwt
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient
from blockchain_routes import blockchain_bp
import requests
from werkzeug.utils import secure_filename
from bson import ObjectId

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(
    app,
    resources={r"/api/*": {"origins": [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]}},
    supports_credentials=True,
    expose_headers=["Authorization", "Content-Type"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
)

# Register blueprints
app.register_blueprint(blockchain_bp)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# MongoDB connection
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/truecred")
mongo_client = MongoClient(mongo_uri)
db = mongo_client.get_default_database()

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default_secret_key")
JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 3600))  # 1 hour
JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", 604800))  # 7 days

# Other configurations
SECRET_KEY = os.getenv("SECRET_KEY", "default_app_secret_key")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

ALLOWED_ORIGINS = {
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
}

@app.before_request
def cors_preflight_handler():
    if request.method == 'OPTIONS' and request.path.startswith('/api/'):
        origin = request.headers.get('Origin')
        resp = make_response('', 200)
        if origin in ALLOWED_ORIGINS:
            resp.headers['Access-Control-Allow-Origin'] = origin
            resp.headers['Vary'] = 'Origin'
            resp.headers['Access-Control-Allow-Credentials'] = 'true'
        # Allow methods and headers
        req_headers = request.headers.get('Access-Control-Request-Headers', 'Authorization,Content-Type')
        resp.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,PATCH,DELETE,OPTIONS'
        resp.headers['Access-Control-Allow-Headers'] = req_headers
        resp.headers['Access-Control-Max-Age'] = '600'
        return resp

@app.after_request
def add_cors_headers(resp):
    # Ensure CORS headers exist on API responses
    if request.path.startswith('/api/'):
        origin = request.headers.get('Origin')
        if origin in ALLOWED_ORIGINS:
            resp.headers.setdefault('Access-Control-Allow-Origin', origin)
            resp.headers.setdefault('Vary', 'Origin')
            resp.headers.setdefault('Access-Control-Allow-Credentials', 'true')
            resp.headers.setdefault('Access-Control-Expose-Headers', 'Authorization,Content-Type')
    return resp

# =======================
# CORS Preflight Handler
# =======================

@app.route('/api/<path:path>', methods=['OPTIONS'])
def api_options(path):
    # Explicitly handle preflight CORS for API endpoints
    resp = make_response('', 204)
    resp.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
    resp.headers['Vary'] = 'Origin'
    resp.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,PATCH,DELETE,OPTIONS'
    resp.headers['Access-Control-Allow-Headers'] = request.headers.get('Access-Control-Request-Headers', 'Authorization,Content-Type')
    resp.headers['Access-Control-Allow-Credentials'] = 'true'
    return resp

# =======================
# Authentication Utilities
# =======================

def generate_token(user_id, token_type="access"):
    """Generate a JWT token for the given user ID."""
    expiration = datetime.utcnow() + timedelta(
        seconds=JWT_ACCESS_TOKEN_EXPIRES if token_type == "access" else JWT_REFRESH_TOKEN_EXPIRES
    )
    
    payload = {
        "user_id": str(user_id),
        "exp": expiration,
        "iat": datetime.utcnow(),
        "type": token_type
    }
    
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")

def token_required(f):
    """Decorator for routes that require a valid token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Let CORS preflight pass through
        if request.method == 'OPTIONS':
            return ('', 204)
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({"error": "Token is missing"}), 401
        
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
            
            if payload.get("type") != "access":
                return jsonify({"error": "Invalid token type"}), 401
            
            # Get user from database (convert string id to ObjectId when possible)
            user_id = payload.get("user_id")
            mongo_id = None
            if isinstance(user_id, str):
                try:
                    mongo_id = ObjectId(user_id)
                except Exception:
                    mongo_id = user_id
            else:
                mongo_id = user_id
            user = db.users.find_one({"_id": mongo_id})
            
            if not user:
                return jsonify({"error": "User not found"}), 401
                
            # Add user to request context
            request.user = user
            
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        
        return f(*args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorator for routes that require admin privileges."""
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        if not request.user.get("is_admin", False):
            return jsonify({"error": "Admin privileges required"}), 403
        return f(*args, **kwargs)
    return decorated

# =======================
# User Routes
# =======================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json(silent=True) or {}
    if not data:
        # Fallback to form data
        data = {
            "email": request.form.get("email"),
            "password": request.form.get("password"),
            "name": request.form.get("name"),
            "role": request.form.get("role"),
        }
    
    # Validate required fields
    required_fields = ["email", "password", "name"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400
    
    # Check if user already exists
    existing_user = db.users.find_one({"email": data["email"]})
    if existing_user:
        return jsonify({"error": "Email already registered"}), 409
    
    # Create new user
    new_user = {
        "email": data["email"],
        "name": data["name"],
        "password_hash": hash_password(data["password"]),  # You'd implement password hashing
        "role": data.get("role", "user"),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "is_active": True,
        "is_verified": False,
        "verification_token": generate_verification_token(),
    }
    
    user_id = db.users.insert_one(new_user).inserted_id
    
    # Send verification email (implement this function)
    send_verification_email(new_user["email"], new_user["verification_token"])
    
    # Generate tokens
    access_token = generate_token(user_id, "access")
    refresh_token = generate_token(user_id, "refresh")
    
    return jsonify({
        "message": "User registered successfully",
        "user": {
            "id": str(user_id),
            "email": new_user["email"],
            "name": new_user["name"],
            "role": new_user["role"],
        },
        "tokens": {
            "access": access_token,
            "refresh": refresh_token,
        }
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login a user."""
    data = request.get_json(silent=True) or {}
    if not data:
        # Fallback to form data
        data = {
            "email": request.form.get("email") or request.form.get("username_or_email"),
            "username_or_email": request.form.get("username_or_email"),
            "password": request.form.get("password"),
        }
    
    # Validate required fields
    email_or_username = data.get("email") or data.get("username_or_email")
    password = data.get("password")
    if not email_or_username or not password:
        return jsonify({"error": "Email and password required"}), 400
    
    # Find user
    # Try finding by email first
    user = db.users.find_one({"email": email_or_username})
    # Optionally support username lookup if your schema includes it
    if not user:
        user = db.users.find_one({"username": email_or_username})
    if not user:
        return jsonify({"error": "Invalid email or password"}), 401
    
    # Verify password (implement verify_password function)
    if not verify_password(password, user["password_hash"]):
        return jsonify({"error": "Invalid email or password"}), 401
    
    # Check if user is active
    if not user.get("is_active", False):
        return jsonify({"error": "Account is inactive"}), 403
    
    # Generate tokens
    access_token = generate_token(user["_id"], "access")
    refresh_token = generate_token(user["_id"], "refresh")
    
    return jsonify({
        "message": "Login successful",
        "user": {
            "id": str(user["_id"]),
            "email": user["email"],
            "name": user["name"],
            "role": user.get("role", "user"),
            "is_verified": user.get("is_verified", False),
        },
        "tokens": {
            "access": access_token,
            "refresh": refresh_token,
        }
    }), 200

@app.route('/api/auth/refresh', methods=['POST'])
def refresh_token():
    """Refresh the access token using a refresh token."""
    refresh_token = request.json.get("refresh_token")
    
    if not refresh_token:
        return jsonify({"error": "Refresh token required"}), 400
    
    try:
        payload = jwt.decode(refresh_token, JWT_SECRET_KEY, algorithms=["HS256"])
        
        if payload.get("type") != "refresh":
            return jsonify({"error": "Invalid token type"}), 401
        
        # Get user from database (convert string id to ObjectId when possible)
        user_id = payload.get("user_id")
        try:
            mongo_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
        except Exception:
            mongo_id = user_id
        user = db.users.find_one({"_id": mongo_id})
        
        if not user:
            return jsonify({"error": "User not found"}), 401
        
        # Generate new access token
        access_token = generate_token(user["_id"], "access")
        
        return jsonify({
            "access_token": access_token,
            "expires_in": JWT_ACCESS_TOKEN_EXPIRES
        }), 200
        
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Refresh token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid refresh token"}), 401

@app.route('/api/auth/verify/<token>', methods=['GET'])
def verify_email(token):
    """Verify a user's email address."""
    user = db.users.find_one({"verification_token": token})
    
    if not user:
        return jsonify({"error": "Invalid verification token"}), 400
    
    # Update user
    db.users.update_one(
        {"_id": user["_id"]},
        {
            "$set": {
                "is_verified": True,
                "verification_token": None,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    # Redirect to frontend
    response = make_response(f"<script>window.location.href = '{FRONTEND_URL}/login?verified=true';</script>")
    response.status_code = 302
    return response

@app.route('/api/user/profile', methods=['GET'])
@token_required
def get_user_profile():
    """Get the current user's profile."""
    user = request.user
    
    return jsonify({
        "id": str(user["_id"]),
        "email": user["email"],
        "name": user["name"],
        "role": user.get("role", "user"),
        "is_verified": user.get("is_verified", False),
        "created_at": user.get("created_at", datetime.utcnow()).isoformat(),
    }), 200

@app.route('/api/user/profile', methods=['PUT'])
@token_required
def update_user_profile():
    """Update the current user's profile."""
    data = request.json
    user = request.user
    
    # Fields that can be updated
    allowed_fields = ["name", "profile_image"]
    update_data = {
        "updated_at": datetime.utcnow()
    }
    
    for field in allowed_fields:
        if field in data:
            update_data[field] = data[field]
    
    # Update user
    db.users.update_one(
        {"_id": user["_id"]},
        {"$set": update_data}
    )
    
    # Get updated user
    updated_user = db.users.find_one({"_id": user["_id"]})
    
    return jsonify({
        "id": str(updated_user["_id"]),
        "email": updated_user["email"],
        "name": updated_user["name"],
        "role": updated_user.get("role", "user"),
        "is_verified": updated_user.get("is_verified", False),
        "created_at": updated_user.get("created_at", datetime.utcnow()).isoformat(),
        "updated_at": updated_user.get("updated_at", datetime.utcnow()).isoformat(),
    }), 200

# =======================
# Credential Routes
# =======================

@app.route('/api/credentials', methods=['POST'])
@token_required
def create_credential():
    """Create a new credential."""
    data = request.json
    user = request.user
    
    # Validate required fields
    required_fields = ["title", "description", "recipient_email", "expiration_date"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400
    
    # Check if user is authorized to issue credentials
    # Treat 'college' as an issuing authority
    if user.get("role") not in ["issuer", "admin", "college"]:
        return jsonify({"error": "Not authorized to issue credentials"}), 403
    
    # Find recipient
    recipient = db.users.find_one({"email": data["recipient_email"]})
    if not recipient:
        return jsonify({"error": "Recipient not found"}), 404
    
    # Create new credential
    new_credential = {
        "title": data["title"],
        "description": data["description"],
        "issuer_id": user["_id"],
        "recipient_id": recipient["_id"],
        "status": "active",
        "issue_date": datetime.utcnow(),
        "expiration_date": datetime.fromisoformat(data["expiration_date"]) if data["expiration_date"] else None,
        "metadata": data.get("metadata", {}),
        "credential_hash": generate_credential_hash(),  # Implement this function
        "blockchain_tx": None,  # Will be updated after blockchain submission
    }
    
    credential_id = db.credentials.insert_one(new_credential).inserted_id
    
    # TODO: Submit credential to blockchain
    # This will be implemented in Phase 2-4
    
    return jsonify({
        "message": "Credential created successfully",
        "credential": {
            "id": str(credential_id),
            "title": new_credential["title"],
            "description": new_credential["description"],
            "status": new_credential["status"],
            "issue_date": new_credential["issue_date"].isoformat(),
            "expiration_date": new_credential["expiration_date"].isoformat() if new_credential["expiration_date"] else None,
        }
    }), 201

@app.route('/api/credentials/<credential_id>', methods=['GET'])
@token_required
def get_credential(credential_id):
    """Get a credential by ID."""
    user = request.user
    
    # Find credential
    try:
        oid = ObjectId(credential_id)
    except Exception:
        return jsonify({"error": "Invalid credential id"}), 400
    credential = db.credentials.find_one({"_id": oid})
    if not credential:
        return jsonify({"error": "Credential not found"}), 404
    
    # Check if user is authorized to view this credential
    if str(credential["issuer_id"]) != str(user["_id"]) and str(credential["recipient_id"]) != str(user["_id"]) and user.get("role") != "admin":
        return jsonify({"error": "Not authorized to view this credential"}), 403
    
    # Get issuer and recipient details
    issuer = db.users.find_one({"_id": credential["issuer_id"]})
    recipient = db.users.find_one({"_id": credential["recipient_id"]})
    
    return jsonify({
        "id": str(credential["_id"]),
        "title": credential["title"],
        "description": credential["description"],
        "status": credential["status"],
        "issue_date": credential["issue_date"].isoformat(),
        "expiration_date": credential["expiration_date"].isoformat() if credential["expiration_date"] else None,
        "issuer": {
            "id": str(issuer["_id"]),
            "name": issuer["name"],
            "email": issuer["email"],
        },
        "recipient": {
            "id": str(recipient["_id"]),
            "name": recipient["name"],
            "email": recipient["email"],
        },
        "metadata": credential.get("metadata", {}),
        "blockchain_tx": credential.get("blockchain_tx"),
    }), 200

@app.route('/api/credentials', methods=['GET'])
@token_required
def get_credentials():
    """Get credentials for the current user."""
    user = request.user
    
    # Get user role
    role = user.get("role", "user")
    
    # Query parameters
    status = request.args.get("status")
    type = request.args.get("type", "all")  # 'issued', 'received', or 'all'
    
    # Build query
    query = {}
    
    if status:
        query["status"] = status
    
    if type == "issued":
        query["issuer_id"] = user["_id"]
    elif type == "received":
        query["recipient_id"] = user["_id"]
    else:
        # If admin, can see all. Otherwise, only see issued or received
        if role != "admin":
            query["$or"] = [
                {"issuer_id": user["_id"]},
                {"recipient_id": user["_id"]}
            ]
    
    # Get credentials
    credentials = list(db.credentials.find(query).sort("issue_date", -1))
    
    # Get all unique user IDs
    user_ids = set()
    for credential in credentials:
        user_ids.add(credential["issuer_id"])
        user_ids.add(credential["recipient_id"])
    
    # Get user details in a single query
    users = {
        str(user["_id"]): user
        for user in db.users.find({"_id": {"$in": list(user_ids)}})
    }
    
    # Format response
    result = []
    for credential in credentials:
        issuer = users.get(str(credential["issuer_id"]), {})
        recipient = users.get(str(credential["recipient_id"]), {})
        
        result.append({
            "id": str(credential["_id"]),
            "title": credential["title"],
            "description": credential["description"],
            "status": credential["status"],
            "issue_date": credential["issue_date"].isoformat(),
            "expiration_date": credential["expiration_date"].isoformat() if credential["expiration_date"] else None,
            "issuer": {
                "id": str(issuer.get("_id", "")),
                "name": issuer.get("name", "Unknown"),
                "email": issuer.get("email", ""),
            },
            "recipient": {
                "id": str(recipient.get("_id", "")),
                "name": recipient.get("name", "Unknown"),
                "email": recipient.get("email", ""),
            },
            "blockchain_tx": credential.get("blockchain_tx"),
        })
    
    return jsonify(result), 200

@app.route('/api/credentials/issued', methods=['GET'])
@token_required
def get_issued_credentials():
    """Get credentials issued by the current user (issuer)."""
    user = request.user
    creds = list(db.credentials.find({"issuer_id": user["_id"]}).sort("issue_date", -1))
    result = [
        {
            "id": str(c.get("_id")),
            "title": c.get("title"),
            "recipientEmail": db.users.find_one({"_id": c.get("recipient_id")}).get("email") if c.get("recipient_id") else "",
            "credentialType": c.get("metadata", {}).get("type") or "degree",
            "issueDate": c.get("issue_date", datetime.utcnow()).isoformat(),
            "status": c.get("status", "active")
        } for c in creds
    ]
    return jsonify({"credentials": result}), 200

@app.route('/api/notifications', methods=['GET'])
@token_required
def get_notifications():
    """Basic notifications endpoint (placeholder)."""
    # In a real app, fetch from a notifications collection
    notifications = []
    return jsonify({"notifications": notifications}), 200

@app.route('/api/ipfs/upload', methods=['POST'])
@token_required
def ipfs_upload():
    """Upload a file to IPFS via configured IPFS API and return ipfs:// URI."""
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "message": "No selected file"}), 400

    ipfs_api = os.getenv('IPFS_API_URL', 'http://127.0.0.1:5001')
    filename = secure_filename(file.filename)
    try:
        files = {'file': (filename, file.stream, file.mimetype)}
        r = requests.post(f"{ipfs_api}/api/v0/add", files=files, timeout=30)
        r.raise_for_status()
        data = r.json()
        ipfs_hash = data.get('Hash') or data.get('hash')
        if not ipfs_hash:
            return jsonify({"success": False, "message": "Invalid IPFS response"}), 502
        return jsonify({"success": True, "ipfs_uri": f"ipfs://{ipfs_hash}"}), 200
    except Exception as e:
        logger.error(f"IPFS upload failed: {e}")
        # Fallback in development
        if os.getenv('FLASK_ENV') == 'development':
            return jsonify({"success": True, "ipfs_uri": "ipfs://mockuri/dev-fallback"}), 200
        return jsonify({"success": False, "message": str(e)}), 502

# ============ Experiences (minimal) ============

@app.route('/api/experiences', methods=['GET'])
@token_required
def get_experiences():
    """List experiences for current user (as owner)."""
    user = request.user
    exps = list(db.experiences.find({"user_id": user["_id"]}).sort("created_at", -1))
    result = [
        {
            "id": str(x.get("_id")),
            "title": x.get("title"),
            "company": x.get("company"),
            "duration": x.get("duration"),
            "status": x.get("status", "pending"),
            "created_at": x.get("created_at", datetime.utcnow()).isoformat()
        } for x in exps
    ]
    return jsonify(result), 200

@app.route('/api/experiences/request', methods=['POST'])
@token_required
def request_experience_verification():
    """Create an experience verification request."""
    data = request.json or {}
    required = ["title", "company", "duration"]
    for f in required:
        if f not in data:
            return jsonify({"error": f"Missing field: {f}"}), 400
    doc = {
        "user_id": request.user["_id"],
        "title": data["title"],
        "company": data["company"],
        "duration": data["duration"],
        "status": "pending",
        "created_at": datetime.utcnow()
    }
    _id = db.experiences.insert_one(doc).inserted_id
    return jsonify({"success": True, "id": str(_id)}), 201

@app.route('/api/experiences/pending', methods=['GET'])
@token_required
def get_pending_experiences():
    """List pending experiences (for company reviewers)."""
    exps = list(db.experiences.find({"status": "pending"}).sort("created_at", -1))
    result = [
        {
            "id": str(x.get("_id")),
            "studentName": db.users.find_one({"_id": x.get("user_id")}).get("name", "Student") if x.get("user_id") else "Student",
            "experienceTitle": x.get("title"),
            "company": x.get("company"),
            "duration": x.get("duration"),
            "submissionDate": x.get("created_at", datetime.utcnow()).strftime('%b %d, %Y')
        } for x in exps
    ]
    return jsonify({"requests": result}), 200

@app.route('/api/experiences/history', methods=['GET'])
@token_required
def get_experiences_history():
    """History of experience verifications (basic)."""
    exps = list(db.experiences.find({"status": {"$in": ["verified", "rejected"]}}).sort("created_at", -1))
    result = [
        {
            "id": str(x.get("_id")),
            "studentName": db.users.find_one({"_id": x.get("user_id")}).get("name", "Student") if x.get("user_id") else "Student",
            "experienceTitle": x.get("title"),
            "status": x.get("status"),
            "actionDate": x.get("updated_at", x.get("created_at", datetime.utcnow())).strftime('%b %d, %Y')
        } for x in exps
    ]
    return jsonify({"history": result}), 200

# ============ College dashboard helpers (minimal) ============

@app.route('/api/college/pending-requests', methods=['GET'])
@token_required
def college_pending_requests():
    """Pending credential requests (placeholder)."""
    # If you have a collection for requests, query it here. Returning empty for now.
    return jsonify({"requests": []}), 200

@app.route('/api/college/verification-history', methods=['GET'])
@token_required
def college_verification_history():
    """Verification history for college (issuer) based on credentials issued."""
    user = request.user
    creds = list(db.credentials.find({"issuer_id": user["_id"]}).sort("issue_date", -1))
    result = [
        {
            "id": str(c.get("_id")),
            "studentName": db.users.find_one({"_id": c.get("recipient_id")}).get("name", "Student") if c.get("recipient_id") else "Student",
            "credentialTitle": c.get("title"),
            "status": c.get("status", "active"),
            "actionDate": c.get("issue_date", datetime.utcnow()).strftime('%b %d, %Y')
        } for c in creds
    ]
    return jsonify({"history": result}), 200

# ============ Company/Experience actions ============

@app.route('/api/experiences/<experience_id>/approve', methods=['POST'])
@token_required
def approve_experience(experience_id):
    """Approve an experience verification request."""
    try:
        oid = ObjectId(experience_id)
    except Exception:
        return jsonify({"error": "Invalid experience id"}), 400
    exp = db.experiences.find_one({"_id": oid})
    if not exp:
        return jsonify({"error": "Experience not found"}), 404
    # TODO: enforce company role/ownership
    db.experiences.update_one({"_id": oid}, {"$set": {"status": "verified", "updated_at": datetime.utcnow()}})
    return jsonify({"success": True}), 200

@app.route('/api/experiences/<experience_id>/reject', methods=['POST'])
@token_required
def reject_experience(experience_id):
    """Reject an experience verification request."""
    try:
        oid = ObjectId(experience_id)
    except Exception:
        return jsonify({"error": "Invalid experience id"}), 400
    exp = db.experiences.find_one({"_id": oid})
    if not exp:
        return jsonify({"error": "Experience not found"}), 404
    reason = (request.json or {}).get('reason')
    db.experiences.update_one({"_id": oid}, {"$set": {"status": "rejected", "rejection_reason": reason, "updated_at": datetime.utcnow()}})
    return jsonify({"success": True}), 200

# ============ College verification request actions (placeholder) ============

@app.route('/api/college/verification-requests/<request_id>', methods=['POST'])
@token_required
def college_verification_action(request_id):
    """Approve/Reject a college verification request (placeholder backing)."""
    # If you later add a collection, update it here. For now, simply acknowledge.
    status = (request.json or {}).get('status')
    if status not in ['Approved', 'Rejected', 'approved', 'rejected']:
        return jsonify({"error": "Invalid status"}), 400
    return jsonify({"success": True}), 200

# ============ Basic user search for StudentLookup ============

@app.route('/api/users/search', methods=['GET'])
@token_required
def search_users():
    """Basic user search by email or wallet for role=student."""
    q = request.args.get('query', '').strip()
    search_type = request.args.get('type', 'email')
    role = request.args.get('role')
    if not q:
        return jsonify({"users": []})
    query = {}
    if role:
        query['role'] = role
    if search_type == 'wallet':
        query['wallet_address'] = {"$regex": q, "$options": "i"}
    else:
        query['email'] = {"$regex": q, "$options": "i"}
    users = list(db.users.find(query).limit(10))
    result = [{
        "id": str(u.get('_id')),
        "name": u.get('name') or u.get('username') or 'User',
        "email": u.get('email', ''),
        "wallet_address": u.get('wallet_address')
    } for u in users]
    return jsonify({"users": result}), 200

@app.route('/api/credentials/<credential_id>/revoke', methods=['POST'])
@token_required
def revoke_credential(credential_id):
    """Revoke a credential."""
    user = request.user
    
    # Find credential
    try:
        oid = ObjectId(credential_id)
    except Exception:
        return jsonify({"error": "Invalid credential id"}), 400
    credential = db.credentials.find_one({"_id": oid})
    if not credential:
        return jsonify({"error": "Credential not found"}), 404
    
    # Check if user is authorized to revoke this credential
    if str(credential["issuer_id"]) != str(user["_id"]) and user.get("role") != "admin":
        return jsonify({"error": "Not authorized to revoke this credential"}), 403
    
    # Check if credential is already revoked
    if credential["status"] == "revoked":
        return jsonify({"error": "Credential is already revoked"}), 400
    
    # Update credential
    db.credentials.update_one(
        {"_id": credential["_id"]},
        {
            "$set": {
                "status": "revoked",
                "revoked_at": datetime.utcnow(),
                "revoked_by": user["_id"],
            }
        }
    )
    
    # TODO: Update credential status on blockchain
    # This will be implemented in Phase 2-4
    
    return jsonify({
        "message": "Credential revoked successfully",
    }), 200

@app.route('/api/credentials/<credential_id>/verify', methods=['GET'])
def verify_credential(credential_id):
    """Verify a credential by ID (public endpoint)."""
    # Find credential
    try:
        oid = ObjectId(credential_id)
    except Exception:
        return jsonify({"error": "Invalid credential id"}), 400
    credential = db.credentials.find_one({"_id": oid})
    if not credential:
        return jsonify({"error": "Credential not found"}), 404
    
    # Check if credential is valid
    is_valid = credential["status"] == "active"
    
    # Check if credential has expired
    if credential["expiration_date"] and credential["expiration_date"] < datetime.utcnow():
        is_valid = False
    
    # Get issuer and recipient details
    issuer = db.users.find_one({"_id": credential["issuer_id"]})
    recipient = db.users.find_one({"_id": credential["recipient_id"]})
    
    # TODO: Verify credential on blockchain (Phase 2-4)
    blockchain_verified = False  # Placeholder until blockchain integration
    
    return jsonify({
        "id": str(credential["_id"]),
        "title": credential["title"],
        "description": credential["description"],
        "is_valid": is_valid,
        "status": credential["status"],
        "issue_date": credential["issue_date"].isoformat(),
        "expiration_date": credential["expiration_date"].isoformat() if credential["expiration_date"] else None,
        "issuer": {
            "name": issuer["name"],
        },
        "recipient": {
            "name": recipient["name"],
        },
        "blockchain_verified": blockchain_verified,
    }), 200

# =======================
# Blockchain Routes (Phase 2-4)
# =======================

@app.route('/api/blockchain/status', methods=['GET'])
def blockchain_status():
    """Get blockchain connection status."""
    try:
        # Placeholder for blockchain connection status
        # This will be implemented in Phase 2-4
        
        # Read contract deployment info if available
        contract_address = os.getenv("CONTRACT_ADDRESS")
        ethereum_network = os.getenv("ETHEREUM_NETWORK", "goerli")
        
        deployment_path = Path(__file__).parent / "build" / "deployment.json"
        deployment_info = {}
        
        if deployment_path.exists():
            with open(deployment_path, "r") as f:
                deployment_info = json.load(f)
        
        return jsonify({
            "connected": True,
            "network": ethereum_network,
            "contract_address": contract_address,
            "deployment_info": deployment_info,
        }), 200
    except Exception as e:
        logger.error(f"Error checking blockchain status: {str(e)}")
        return jsonify({
            "connected": False,
            "error": str(e),
        }), 500

# =======================
# Main Application Entry
# =======================

@app.route('/', methods=['GET'])
def index():
    """Root endpoint."""
    return jsonify({
        "name": "TrueCred API",
        "version": "1.0.0",
        "status": "running",
    }), 200

# Placeholder functions (to be implemented)
def hash_password(password):
    """Hash a password."""
    # This would use a proper hashing algorithm like bcrypt
    return f"hashed_{password}"

def verify_password(password, password_hash):
    """Verify a password against a hash."""
    # This would use a proper password verification
    return password_hash == f"hashed_{password}"

def generate_verification_token():
    """Generate a verification token."""
    # This would generate a secure random token
    import secrets
    return secrets.token_urlsafe(32)

def send_verification_email(email, token):
    """Send a verification email."""
    # This would send an actual email
    verification_url = f"{FRONTEND_URL}/verify/{token}"
    logger.info(f"Verification email would be sent to {email} with URL: {verification_url}")

def generate_credential_hash():
    """Generate a unique hash for a credential."""
    # This would generate a secure hash
    import secrets
    return secrets.token_hex(16)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

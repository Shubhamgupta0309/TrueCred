#!/usr/bin/env python3
"""
Blockchain API Routes for TrueCred
Provides RESTful API endpoints for interacting with the blockchain.
"""
from flask import Blueprint, jsonify, request
from functools import wraps

from blockchain_service import blockchain_service

# Create blueprint
blockchain_bp = Blueprint('blockchain', __name__, url_prefix='/api/blockchain')

# Helper for checking blockchain connection
def blockchain_connected(f):
    """Decorator to check if blockchain is connected."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not blockchain_service.is_connected():
            return jsonify({
                "error": "Blockchain not connected",
                "details": "The blockchain service is not properly connected. Check configuration."
            }), 503
        return f(*args, **kwargs)
    return decorated

# =======================
# Status Endpoints
# =======================

@blockchain_bp.route('/status', methods=['GET'])
def status():
    """Get blockchain connection status."""
    status = blockchain_service.get_connection_status()
    return jsonify(status), 200

# =======================
# Credential Endpoints
# =======================

@blockchain_bp.route('/credentials/issue', methods=['POST'])
@blockchain_connected
def issue_credential():
    """Issue a new credential on the blockchain."""
    data = request.json
    
    # Validate required fields
    required_fields = ["subject", "credential_type", "metadata_uri"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400
    
    # Optional fields
    expiration_date = data.get("expiration_date", 0)
    
    # Issue credential
    result = blockchain_service.issue_credential(
        subject=data["subject"],
        credential_type=data["credential_type"],
        metadata_uri=data["metadata_uri"],
        expiration_date=expiration_date
    )
    
    if not result:
        return jsonify({
            "error": "Failed to issue credential",
            "details": "The blockchain service encountered an error."
        }), 500
    
    if result.get("status") == "error":
        return jsonify({
            "error": "Failed to issue credential",
            "details": result.get("error", "Unknown error")
        }), 500
    
    return jsonify({
        "message": "Credential issued successfully",
        "transaction_hash": result["transaction_hash"],
        "credential_id": result["credential_id"]
    }), 201

@blockchain_bp.route('/credentials/batch-issue', methods=['POST'])
@blockchain_connected
def batch_issue_credentials():
    """Issue multiple credentials in a batch."""
    data = request.json
    
    # Validate required fields
    required_fields = ["subjects", "credential_types", "metadata_uris"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400
    
    # Optional fields
    expiration_dates = data.get("expiration_dates", [0] * len(data["subjects"]))
    
    # Validate array lengths
    if not (len(data["subjects"]) == len(data["credential_types"]) == len(data["metadata_uris"])):
        return jsonify({
            "error": "Invalid input",
            "details": "Input arrays must have the same length"
        }), 400
    
    # Issue credentials
    result = blockchain_service.batch_issue_credentials(
        subjects=data["subjects"],
        credential_types=data["credential_types"],
        metadata_uris=data["metadata_uris"],
        expiration_dates=expiration_dates
    )
    
    if not result:
        return jsonify({
            "error": "Failed to issue credentials",
            "details": "The blockchain service encountered an error."
        }), 500
    
    if result.get("status") == "error":
        return jsonify({
            "error": "Failed to issue credentials",
            "details": result.get("error", "Unknown error")
        }), 500
    
    return jsonify({
        "message": "Credentials issued successfully",
        "transaction_hash": result["transaction_hash"],
        "credential_ids": result["credential_ids"]
    }), 201

@blockchain_bp.route('/credentials/revoke', methods=['POST'])
@blockchain_connected
def revoke_credential():
    """Revoke a credential on the blockchain."""
    data = request.json
    
    # Validate required fields
    if "credential_id" not in data:
        return jsonify({"error": "Missing field: credential_id"}), 400
    
    # Convert credential_id to bytes if it's hex
    credential_id = data["credential_id"]
    if credential_id.startswith("0x"):
        credential_id = bytes.fromhex(credential_id[2:])
    
    # Revoke credential
    result = blockchain_service.revoke_credential(credential_id)
    
    if not result:
        return jsonify({
            "error": "Failed to revoke credential",
            "details": "The blockchain service encountered an error."
        }), 500
    
    if result.get("status") == "error":
        return jsonify({
            "error": "Failed to revoke credential",
            "details": result.get("error", "Unknown error")
        }), 500
    
    return jsonify({
        "message": "Credential revoked successfully",
        "transaction_hash": result["transaction_hash"]
    }), 200

@blockchain_bp.route('/credentials/verify', methods=['POST'])
@blockchain_connected
def verify_credential():
    """Verify a credential's validity on the blockchain."""
    data = request.json
    
    # Validate required fields
    if "credential_id" not in data:
        return jsonify({"error": "Missing field: credential_id"}), 400
    
    # Convert credential_id to bytes if it's hex
    credential_id = data["credential_id"]
    if credential_id.startswith("0x"):
        credential_id = bytes.fromhex(credential_id[2:])
    
    # Verify credential
    result = blockchain_service.verify_credential(credential_id)
    
    if not result:
        return jsonify({
            "error": "Failed to verify credential",
            "details": "The blockchain service encountered an error."
        }), 500
    
    if result.get("status") == "error":
        return jsonify({
            "error": "Failed to verify credential",
            "details": result.get("error", "Unknown error")
        }), 500
    
    return jsonify(result), 200

@blockchain_bp.route('/credentials/details', methods=['POST'])
@blockchain_connected
def get_credential_details():
    """Get detailed information about a credential."""
    data = request.json
    
    # Validate required fields
    if "credential_id" not in data:
        return jsonify({"error": "Missing field: credential_id"}), 400
    
    # Convert credential_id to bytes if it's hex
    credential_id = data["credential_id"]
    if credential_id.startswith("0x"):
        credential_id = bytes.fromhex(credential_id[2:])
    
    # Get credential details
    result = blockchain_service.get_credential_details(credential_id)
    
    if not result:
        return jsonify({
            "error": "Failed to get credential details",
            "details": "The blockchain service encountered an error."
        }), 500
    
    if result.get("status") == "error":
        return jsonify({
            "error": "Failed to get credential details",
            "details": result.get("error", "Unknown error")
        }), 500
    
    return jsonify(result), 200

@blockchain_bp.route('/credentials/subject/<subject_address>', methods=['GET'])
@blockchain_connected
def get_subject_credentials(subject_address):
    """Get all credential IDs owned by a subject."""
    # Get subject credentials
    result = blockchain_service.get_subject_credentials(subject_address)
    
    if result is None:
        return jsonify({
            "error": "Failed to get subject credentials",
            "details": "The blockchain service encountered an error."
        }), 500
    
    return jsonify({
        "subject": subject_address,
        "credential_ids": result
    }), 200

@blockchain_bp.route('/credentials/issuer/<issuer_address>', methods=['GET'])
@blockchain_connected
def get_issuer_credentials(issuer_address):
    """Get all credential IDs issued by an issuer."""
    # Get issuer credentials
    result = blockchain_service.get_issuer_credentials(issuer_address)
    
    if result is None:
        return jsonify({
            "error": "Failed to get issuer credentials",
            "details": "The blockchain service encountered an error."
        }), 500
    
    return jsonify({
        "issuer": issuer_address,
        "credential_ids": result
    }), 200

# =======================
# Issuer Endpoints
# =======================

@blockchain_bp.route('/issuers/check/<issuer_address>', methods=['GET'])
@blockchain_connected
def is_authorized_issuer(issuer_address):
    """Check if an address is an authorized issuer."""
    # Check if issuer is authorized
    is_authorized = blockchain_service.is_authorized_issuer(issuer_address)
    
    return jsonify({
        "issuer": issuer_address,
        "is_authorized": is_authorized
    }), 200

@blockchain_bp.route('/issuers/authorize', methods=['POST'])
@blockchain_connected
def authorize_issuer():
    """Authorize an address to issue credentials."""
    data = request.json
    
    # Validate required fields
    if "issuer" not in data:
        return jsonify({"error": "Missing field: issuer"}), 400
    
    # Authorize issuer
    result = blockchain_service.authorize_issuer(data["issuer"])
    
    if not result:
        return jsonify({
            "error": "Failed to authorize issuer",
            "details": "The blockchain service encountered an error."
        }), 500
    
    if result.get("status") == "error":
        return jsonify({
            "error": "Failed to authorize issuer",
            "details": result.get("error", "Unknown error")
        }), 500
    
    return jsonify({
        "message": "Issuer authorized successfully",
        "transaction_hash": result["transaction_hash"]
    }), 200

@blockchain_bp.route('/issuers/revoke', methods=['POST'])
@blockchain_connected
def revoke_issuer():
    """Revoke an issuer's authorization."""
    data = request.json
    
    # Validate required fields
    if "issuer" not in data:
        return jsonify({"error": "Missing field: issuer"}), 400
    
    # Revoke issuer
    result = blockchain_service.revoke_issuer(data["issuer"])
    
    if not result:
        return jsonify({
            "error": "Failed to revoke issuer",
            "details": "The blockchain service encountered an error."
        }), 500
    
    if result.get("status") == "error":
        return jsonify({
            "error": "Failed to revoke issuer",
            "details": result.get("error", "Unknown error")
        }), 500
    
    return jsonify({
        "message": "Issuer revoked successfully",
        "transaction_hash": result["transaction_hash"]
    }), 200

# =======================
# Signing Endpoints
# =======================

@blockchain_bp.route('/sign', methods=['POST'])
@blockchain_connected
def sign_message():
    """Sign a message with the account's private key."""
    data = request.json
    
    # Validate required fields
    if "message" not in data:
        return jsonify({"error": "Missing field: message"}), 400
    
    # Sign message
    result = blockchain_service.sign_message(data["message"])
    
    if not result:
        return jsonify({
            "error": "Failed to sign message",
            "details": "The blockchain service encountered an error."
        }), 500
    
    if result.get("status") == "error":
        return jsonify({
            "error": "Failed to sign message",
            "details": result.get("error", "Unknown error")
        }), 500
    
    return jsonify(result), 200

@blockchain_bp.route('/verify-signature', methods=['POST'])
@blockchain_connected
def verify_signature():
    """Verify a signature."""
    data = request.json
    
    # Validate required fields
    required_fields = ["message", "signature", "address"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400
    
    # Verify signature
    is_valid = blockchain_service.verify_signature(
        data["message"],
        data["signature"],
        data["address"]
    )
    
    return jsonify({
        "is_valid": is_valid
    }), 200

# Register the blueprint in app.py like this:
# from blockchain_routes import blockchain_bp
# app.register_blueprint(blockchain_bp)

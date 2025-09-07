"""
Update to the API Documentation for the TrueCred API to include Verification endpoints.
"""

# We'll add this to the existing API_ENDPOINTS dictionary in api_docs.py
VERIFICATION_ENDPOINTS = {
    "Verification": [
        {
            "path": "/api/verification/experience/request/{experience_id}",
            "method": "POST",
            "description": "Request verification for an experience",
            "auth": True,
            "request_body": {
                "verification_data": "Optional additional data about the verification request"
            },
            "responses": {
                "200": "Verification request submitted successfully",
                "400": "Invalid request or experience already verified/pending",
                "401": "Unauthorized",
                "403": "User does not own the experience",
                "404": "Experience not found"
            }
        },
        {
            "path": "/api/verification/experience/verify/{experience_id}",
            "method": "POST",
            "description": "Verify an experience (requires verifier or admin role)",
            "auth": True,
            "request_body": {
                "verification_data": "Optional additional data about the verification"
            },
            "responses": {
                "200": "Experience verified successfully",
                "400": "Invalid request or experience already verified",
                "401": "Unauthorized",
                "403": "User does not have verification permissions",
                "404": "Experience not found"
            }
        },
        {
            "path": "/api/verification/experience/reject/{experience_id}",
            "method": "POST",
            "description": "Reject verification for an experience (requires verifier or admin role)",
            "auth": True,
            "request_body": {
                "reason": "Required reason for rejection",
                "verification_data": "Optional additional data about the rejection"
            },
            "responses": {
                "200": "Experience verification rejected",
                "400": "Invalid request or experience not pending verification",
                "401": "Unauthorized",
                "403": "User does not have verification permissions",
                "404": "Experience not found"
            }
        },
        {
            "path": "/api/verification/credential/request/{credential_id}",
            "method": "POST",
            "description": "Request verification for a credential",
            "auth": True,
            "request_body": {
                "verification_data": "Optional additional data about the verification request"
            },
            "responses": {
                "200": "Verification request submitted successfully",
                "400": "Invalid request or credential already verified/pending",
                "401": "Unauthorized",
                "403": "User does not own the credential",
                "404": "Credential not found"
            }
        },
        {
            "path": "/api/verification/credential/verify/{credential_id}",
            "method": "POST",
            "description": "Verify a credential (requires verifier or admin role)",
            "auth": True,
            "request_body": {
                "verification_data": "Optional additional data about the verification"
            },
            "responses": {
                "200": "Credential verified successfully",
                "400": "Invalid request or credential already verified",
                "401": "Unauthorized",
                "403": "User does not have verification permissions",
                "404": "Credential not found"
            }
        },
        {
            "path": "/api/verification/credential/reject/{credential_id}",
            "method": "POST",
            "description": "Reject verification for a credential (requires verifier or admin role)",
            "auth": True,
            "request_body": {
                "reason": "Required reason for rejection",
                "verification_data": "Optional additional data about the rejection"
            },
            "responses": {
                "200": "Credential verification rejected",
                "400": "Invalid request or credential not pending verification",
                "401": "Unauthorized",
                "403": "User does not have verification permissions",
                "404": "Credential not found"
            }
        },
        {
            "path": "/api/verification/pending",
            "method": "GET",
            "description": "Get all pending verifications (requires verifier or admin role)",
            "auth": True,
            "query_params": {
                "type": "Optional type of verification (experience or credential)",
                "user_id": "Optional user ID to filter by"
            },
            "responses": {
                "200": "Pending verifications retrieved successfully",
                "401": "Unauthorized",
                "403": "User does not have verification permissions"
            }
        },
        {
            "path": "/api/verification/link/{credential_id}/experience/{experience_id}",
            "method": "POST",
            "description": "Link a credential to an experience",
            "auth": True,
            "responses": {
                "200": "Credential linked to experience successfully",
                "401": "Unauthorized",
                "403": "User does not own both the credential and experience",
                "404": "Credential or experience not found"
            }
        },
        {
            "path": "/api/verification/unlink/{credential_id}/experience/{experience_id}",
            "method": "POST",
            "description": "Unlink a credential from an experience",
            "auth": True,
            "responses": {
                "200": "Credential unlinked from experience successfully",
                "401": "Unauthorized",
                "403": "User does not own both the credential and experience",
                "404": "Credential or experience not found"
            }
        }
    ]
}

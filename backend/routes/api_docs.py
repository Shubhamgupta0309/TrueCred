"""
API Documentation for the TrueCred API.

This module provides a structured overview of all API endpoints.
"""
from routes.verification_docs import VERIFICATION_ENDPOINTS

API_ENDPOINTS = {
    "Authentication": [
        {
            "path": "/api/auth/register",
            "method": "POST",
            "description": "Register a new user",
            "request_body": {
                "username": "Unique username",
                "email": "User's email address",
                "password": "Password",
                "first_name": "User's first name (optional)",
                "last_name": "User's last name (optional)"
            },
            "responses": {
                "201": "User registered successfully",
                "400": "Invalid request data"
            }
        },
        {
            "path": "/api/auth/login",
            "method": "POST",
            "description": "Authenticate a user and return a JWT token",
            "request_body": {
                "username_or_email": "Username or email",
                "password": "Password"
            },
            "responses": {
                "200": "Login successful",
                "401": "Invalid credentials"
            }
        },
        {
            "path": "/api/auth/logout",
            "method": "POST",
            "description": "Logout a user by blacklisting their JWT token",
            "auth": True,
            "responses": {
                "200": "Successfully logged out",
                "401": "Unauthorized"
            }
        },
        {
            "path": "/api/auth/profile",
            "method": "GET",
            "description": "Get the current user's profile",
            "auth": True,
            "responses": {
                "200": "User profile data",
                "401": "Unauthorized"
            }
        },
        {
            "path": "/api/auth/profile",
            "method": "PUT",
            "description": "Update the current user's profile",
            "auth": True,
            "request_body": {
                "first_name": "User's first name (optional)",
                "last_name": "User's last name (optional)",
                "email": "User's email address (optional)"
            },
            "responses": {
                "200": "Profile updated successfully",
                "400": "Invalid request data",
                "401": "Unauthorized"
            }
        },
        {
            "path": "/api/auth/change-password",
            "method": "POST",
            "description": "Change the current user's password",
            "auth": True,
            "request_body": {
                "current_password": "User's current password",
                "new_password": "User's new password"
            },
            "responses": {
                "200": "Password changed successfully",
                "400": "Invalid request data",
                "401": "Unauthorized"
            }
        },
        {
            "path": "/api/auth/forgot-password",
            "method": "POST",
            "description": "Request a password reset",
            "request_body": {
                "email": "User's email address"
            },
            "responses": {
                "200": "Password reset link sent",
                "400": "Invalid request data"
            }
        },
        {
            "path": "/api/auth/reset-password",
            "method": "POST",
            "description": "Reset a password using a reset token",
            "request_body": {
                "token": "Password reset token",
                "new_password": "New password"
            },
            "responses": {
                "200": "Password has been reset successfully",
                "400": "Invalid request data"
            }
        },
        {
            "path": "/api/auth/refresh",
            "method": "POST",
            "description": "Refresh an expired access token",
            "auth": "refresh",
            "responses": {
                "200": "New access token",
                "401": "Unauthorized"
            }
        }
    ],
    "User Management (Admin)": [
        {
            "path": "/api/auth/users",
            "method": "GET",
            "description": "Get all users (admin only)",
            "auth": "admin",
            "responses": {
                "200": "List of all users",
                "401": "Unauthorized",
                "403": "Forbidden"
            }
        },
        {
            "path": "/api/auth/users/{user_id}",
            "method": "GET",
            "description": "Get a specific user by ID (admin only)",
            "auth": "admin",
            "responses": {
                "200": "User profile data",
                "401": "Unauthorized",
                "403": "Forbidden",
                "404": "User not found"
            }
        },
        {
            "path": "/api/auth/users/{user_id}",
            "method": "PUT",
            "description": "Update a specific user (admin only)",
            "auth": "admin",
            "request_body": {
                "first_name": "User's first name (optional)",
                "last_name": "User's last name (optional)",
                "email": "User's email address (optional)",
                "is_active": "User's active status (optional)",
                "role": "User's role (optional)"
            },
            "responses": {
                "200": "User updated successfully",
                "400": "Invalid request data",
                "401": "Unauthorized",
                "403": "Forbidden",
                "404": "User not found"
            }
        },
        {
            "path": "/api/auth/users/{user_id}",
            "method": "DELETE",
            "description": "Deactivate a user (soft delete) (admin only)",
            "auth": "admin",
            "responses": {
                "200": "User deactivated successfully",
                "401": "Unauthorized",
                "403": "Forbidden",
                "404": "User not found"
            }
        }
    ],
    "Credentials": [
        {
            "path": "/api/credentials",
            "method": "GET",
            "description": "Get all credentials for the current user",
            "auth": True,
            "responses": {
                "200": "List of credentials",
                "401": "Unauthorized"
            }
        },
        {
            "path": "/api/credentials/{credential_id}",
            "method": "GET",
            "description": "Get a specific credential by ID",
            "auth": True,
            "responses": {
                "200": "Credential data",
                "401": "Unauthorized",
                "404": "Credential not found"
            }
        },
        {
            "path": "/api/credentials",
            "method": "POST",
            "description": "Create a new credential",
            "auth": "issuer",
            "request_body": {
                "recipient_id": "ID of the credential recipient",
                "credential_type": "Type of credential",
                "credential_data": "Credential data",
                "expiration_date": "Expiration date (optional)"
            },
            "responses": {
                "201": "Credential created successfully",
                "400": "Invalid request data",
                "401": "Unauthorized",
                "403": "Forbidden"
            }
        },
        {
            "path": "/api/credentials/{credential_id}",
            "method": "PUT",
            "description": "Update a credential",
            "auth": "issuer",
            "request_body": {
                "credential_data": "Updated credential data",
                "expiration_date": "Updated expiration date (optional)"
            },
            "responses": {
                "200": "Credential updated successfully",
                "400": "Invalid request data",
                "401": "Unauthorized",
                "403": "Forbidden",
                "404": "Credential not found"
            }
        },
        {
            "path": "/api/credentials/{credential_id}",
            "method": "DELETE",
            "description": "Revoke a credential",
            "auth": "issuer",
            "responses": {
                "200": "Credential revoked successfully",
                "401": "Unauthorized",
                "403": "Forbidden",
                "404": "Credential not found"
            }
        },
        {
            "path": "/api/credentials/verify/{credential_id}",
            "method": "GET",
            "description": "Verify a credential",
            "responses": {
                "200": "Credential verification result",
                "404": "Credential not found"
            }
        }
    ],
    "Experiences": [
        {
            "path": "/api/experiences",
            "method": "GET",
            "description": "Get all experiences for the current user",
            "auth": True,
            "responses": {
                "200": "List of experiences",
                "401": "Unauthorized"
            }
        },
        {
            "path": "/api/experiences/{experience_id}",
            "method": "GET",
            "description": "Get a specific experience by ID",
            "auth": True,
            "responses": {
                "200": "Experience data",
                "401": "Unauthorized",
                "404": "Experience not found"
            }
        },
        {
            "path": "/api/experiences",
            "method": "POST",
            "description": "Create a new experience",
            "auth": True,
            "request_body": {
                "title": "Experience title",
                "organization": "Organization name",
                "description": "Experience description",
                "start_date": "Start date",
                "end_date": "End date (optional)",
                "credential_ids": "List of credential IDs (optional)"
            },
            "responses": {
                "201": "Experience created successfully",
                "400": "Invalid request data",
                "401": "Unauthorized"
            }
        },
        {
            "path": "/api/experiences/{experience_id}",
            "method": "PUT",
            "description": "Update an experience",
            "auth": True,
            "request_body": {
                "title": "Updated experience title (optional)",
                "organization": "Updated organization name (optional)",
                "description": "Updated experience description (optional)",
                "start_date": "Updated start date (optional)",
                "end_date": "Updated end date (optional)",
                "credential_ids": "Updated list of credential IDs (optional)"
            },
            "responses": {
                "200": "Experience updated successfully",
                "400": "Invalid request data",
                "401": "Unauthorized",
                "404": "Experience not found"
            }
        },
        {
            "path": "/api/experiences/{experience_id}",
            "method": "DELETE",
            "description": "Delete an experience",
            "auth": True,
            "responses": {
                "200": "Experience deleted successfully",
                "401": "Unauthorized",
                "404": "Experience not found"
            }
        }
    ],
    "Search": [
        {
            "path": "/api/search",
            "method": "GET",
            "description": "Perform a combined search across credentials and experiences",
            "auth": True,
            "query_params": {
                "q": "Search query (required)",
                "include_credentials": "Include credentials in search (true/false, default: true)",
                "include_experiences": "Include experiences in search (true/false, default: true)",
                "page": "Page number (default: 1)",
                "per_page": "Results per page (default: 10, max: 50)"
            },
            "responses": {
                "200": "Combined search results with pagination metadata",
                "400": "Invalid search parameters",
                "401": "Unauthorized"
            }
        },
        {
            "path": "/api/search/credentials",
            "method": "GET",
            "description": "Search credentials with filters and pagination",
            "auth": True,
            "query_params": {
                "q": "Search query for title, description",
                "issuer": "Filter by issuer",
                "type": "Filter by credential type",
                "verified": "Filter by verification status (true/false)",
                "include_expired": "Include expired credentials (true/false)",
                "start_date": "Filter by issue date (from) in ISO format",
                "end_date": "Filter by issue date (to) in ISO format",
                "sort_by": "Field to sort by (prepend with - for descending)",
                "page": "Page number (default: 1)",
                "per_page": "Results per page (default: 10, max: 50)"
            },
            "responses": {
                "200": "Credential search results with pagination metadata",
                "400": "Invalid search parameters",
                "401": "Unauthorized"
            }
        },
        {
            "path": "/api/search/experiences",
            "method": "GET",
            "description": "Search experiences with filters and pagination",
            "auth": True,
            "query_params": {
                "q": "Search query for title, description, organization",
                "organization": "Filter by organization",
                "type": "Filter by experience type (work, education)",
                "current": "Filter by current status (true/false)",
                "verified": "Filter by verification status (true/false)",
                "has_credentials": "Filter to experiences with linked credentials (true/false)",
                "start_date": "Filter by start date (from) in ISO format",
                "end_date": "Filter by start date (to) in ISO format",
                "sort_by": "Field to sort by (prepend with - for descending)",
                "page": "Page number (default: 1)",
                "per_page": "Results per page (default: 10, max: 50)"
            },
            "responses": {
                "200": "Experience search results with pagination metadata",
                "400": "Invalid search parameters",
                "401": "Unauthorized"
            }
        }
    ],
    "Document Management": [
        {
            "path": "/api/documents/upload",
            "method": "POST",
            "description": "Upload a document and store it on IPFS",
            "auth": True,
            "content_type": "multipart/form-data",
            "request_body": {
                "file": "Document file (PDF, DOC, DOCX, JPG, JPEG, PNG, TXT)",
                "document_type": "Type of document (degree, transcript, certificate, etc.)",
                "title": "Document title",
                "description": "Optional description",
                "is_public": "Whether document should be publicly accessible (true/false)"
            },
            "responses": {
                "200": "Document uploaded successfully",
                "400": "Invalid file or request data",
                "401": "Unauthorized",
                "413": "File too large"
            }
        },
        {
            "path": "/api/documents/{document_id}",
            "method": "GET",
            "description": "Get document metadata and access information",
            "auth": True,
            "responses": {
                "200": "Document metadata and IPFS access URL",
                "401": "Unauthorized",
                "403": "Access denied",
                "404": "Document not found"
            }
        },
        {
            "path": "/api/documents/{document_id}/download",
            "method": "GET",
            "description": "Download document from IPFS",
            "auth": True,
            "responses": {
                "200": "Document file data",
                "401": "Unauthorized",
                "403": "Access denied",
                "404": "Document not found"
            }
        },
        {
            "path": "/api/documents/{document_id}/verify",
            "method": "POST",
            "description": "Manually verify or reject a document",
            "auth": "issuer",
            "request_body": {
                "verification_status": "'verified' or 'rejected'",
                "comments": "Verification comments",
                "verified_by": "Name/ID of verifier"
            },
            "responses": {
                "200": "Document verification updated",
                "400": "Invalid verification data",
                "401": "Unauthorized",
                "403": "Insufficient permissions",
                "404": "Document not found"
            }
        },
        {
            "path": "/api/documents/{document_id}/blockchain-status",
            "method": "GET",
            "description": "Get blockchain storage status for a document",
            "auth": True,
            "responses": {
                "200": "Blockchain status information",
                "401": "Unauthorized",
                "404": "Document not found"
            }
        },
        {
            "path": "/api/documents/user/{user_id}",
            "method": "GET",
            "description": "Get all documents for a specific user",
            "auth": True,
            "responses": {
                "200": "List of user's documents",
                "401": "Unauthorized",
                "403": "Access denied"
            }
        },
        {
            "path": "/api/documents/pending-verification",
            "method": "GET",
            "description": "Get documents pending verification (for issuers)",
            "auth": "issuer",
            "query_params": {
                "limit": "Maximum number of documents (default: 50)",
                "offset": "Number of documents to skip (default: 0)"
            },
            "responses": {
                "200": "List of pending documents",
                "401": "Unauthorized",
                "403": "Insufficient permissions"
            }
        },
        {
            "path": "/api/documents/{document_id}/share",
            "method": "POST",
            "description": "Generate a shareable link for a document",
            "auth": True,
            "request_body": {
                "expires_in": "Expiration time in hours (optional)",
                "access_level": "'view' or 'download' (optional)"
            },
            "responses": {
                "200": "Share link generated",
                "401": "Unauthorized",
                "403": "Access denied",
                "404": "Document not found"
            }
        }
    ],
    "Manual Verification": [
        {
            "path": "/api/verification/pending",
            "method": "GET",
            "description": "Get all documents pending verification",
            "auth": "issuer",
            "query_params": {
                "limit": "Maximum number of documents (default: 50)",
                "offset": "Number of documents to skip (default: 0)",
                "document_type": "Filter by document type"
            },
            "responses": {
                "200": "List of pending verifications",
                "401": "Unauthorized",
                "403": "Insufficient permissions"
            }
        },
        {
            "path": "/api/verification/{document_id}/review",
            "method": "POST",
            "description": "Review and verify/reject a document",
            "auth": "issuer",
            "request_body": {
                "action": "'verify' or 'reject'",
                "comments": "Review comments (required for rejection)",
                "verification_details": "Additional verification details",
                "store_on_blockchain": "Store verified document on blockchain (default: true)"
            },
            "responses": {
                "200": "Document reviewed successfully",
                "400": "Invalid review data",
                "401": "Unauthorized",
                "403": "Insufficient permissions",
                "404": "Document not found"
            }
        },
        {
            "path": "/api/verification/stats",
            "method": "GET",
            "description": "Get verification statistics for the current user",
            "auth": "issuer",
            "responses": {
                "200": "Verification statistics",
                "401": "Unauthorized",
                "403": "Insufficient permissions"
            }
        },
        {
            "path": "/api/verification/bulk-review",
            "method": "POST",
            "description": "Review multiple documents at once",
            "auth": "issuer",
            "request_body": {
                "document_ids": "List of document IDs to review",
                "action": "'verify' or 'reject'",
                "comments": "Review comments (required for rejection)",
                "store_on_blockchain": "Store verified documents on blockchain (default: true)"
            },
            "responses": {
                "200": "Bulk review completed",
                "400": "Invalid bulk review data",
                "401": "Unauthorized",
                "403": "Insufficient permissions"
            }
        },
        {
            "path": "/api/verification/credential-requests",
            "method": "GET",
            "description": "Get credential requests that need manual verification",
            "auth": "issuer",
            "query_params": {
                "status": "Filter by status (pending, approved, rejected)",
                "limit": "Maximum number of requests (default: 50)",
                "offset": "Number of requests to skip (default: 0)"
            },
            "responses": {
                "200": "List of credential requests",
                "401": "Unauthorized",
                "403": "Insufficient permissions"
            }
        }
    ],
    "Health Check": [
        {
            "path": "/api/health",
            "method": "GET",
            "description": "Basic health check endpoint",
            "responses": {
                "200": "API is healthy"
            }
        },
        {
            "path": "/api/health/check",
            "method": "GET",
            "description": "Detailed health check endpoint",
            "responses": {
                "200": "All systems operational",
                "207": "Some systems degraded",
                "500": "Health check failed"
            }
        }
    ],
    "API Info": [
        {
            "path": "/api",
            "method": "GET",
            "description": "API index route with basic information",
            "responses": {
                "200": "API information"
            }
        },
        {
            "path": "/api/status",
            "method": "GET",
            "description": "API status route with operational status",
            "responses": {
                "200": "API status information"
            }
        }
    ]
}

# Update API_ENDPOINTS with verification endpoints
API_ENDPOINTS.update(VERIFICATION_ENDPOINTS)

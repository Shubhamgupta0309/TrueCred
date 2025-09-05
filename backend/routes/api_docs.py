"""
API Documentation for the TrueCred API.

This module provides a structured overview of all API endpoints.
"""

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

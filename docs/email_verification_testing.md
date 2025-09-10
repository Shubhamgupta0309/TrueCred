# Testing Email Verification

This document explains how to test the email verification system in the TrueCred application.

## Overview

TrueCred uses email verification to ensure users provide valid email addresses. In a production environment, verification links would be sent via email. For development and testing purposes, we've implemented a test tool to simplify this process.

## Testing the Verification Flow

### Method 1: Manual Testing

1. Register a new account
2. Try logging in - you'll see a verification reminder
3. Check the backend logs to see the verification token
4. Manually visit `/verify-email?token=YOUR_TOKEN` with the token from the logs

### Method 2: Using the Test Tool

For easier testing, we've added a test verification tool:

1. Visit `/test-verification` in the browser
2. Enter the email address of a registered user
3. Click "Generate Verification Link"
4. Use the "Open Verification Link" button to navigate to the verification page

Note: The test tool only works in development mode and requires the backend to be running with `DEBUG=True`.

## Development Endpoints

The backend provides a special development-only endpoint at `/api/dev/get-verification-token` that allows retrieving verification tokens for testing purposes. This endpoint is automatically disabled in production mode for security.

## Verification Process

1. When a user registers, a verification token is generated and stored in the database
2. The token is valid for 7 days
3. When the verification link is visited, the token is validated
4. If valid, the user's email is marked as verified
5. After successful verification, the user is automatically logged in

## Verification Reminder

The application shows a verification reminder when an unverified user attempts to log in. From this reminder, users can:

1. Request a new verification email (which generates a new token)
2. Return to login

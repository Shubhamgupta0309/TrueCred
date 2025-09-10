# Email Verification System for TrueCred

This document outlines the email verification system implemented in the TrueCred application.

## Overview

The email verification system ensures that users provide valid email addresses during registration and helps prevent fraud by verifying email ownership. The system consists of:

1. **Backend Components**:

   - Token generation and storage
   - Email sending via SMTP
   - Token verification endpoints
   - User status management

2. **Frontend Components**:
   - Verification reminder UI
   - Verification page
   - Test tools for development

## How It Works

### Registration Process

1. User registers with email and password
2. Backend generates a verification token and stores it with the user
3. Verification email is sent via SMTP
4. User cannot access protected features until email is verified

### Verification Process

1. User clicks link in email, which contains the verification token
2. Frontend routes to verification page with token in URL
3. Verification page sends token to backend for validation
4. If valid, backend marks user as verified and returns success
5. User is redirected to appropriate dashboard

## Configuration

### Backend Configuration (.env)

```
# Email configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=your.email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=TrueCred <your.email@gmail.com>

# Frontend URL for verification links
FRONTEND_URL=http://localhost:5173
```

### Gmail App Password

For Gmail, you need to use an App Password instead of your regular password:

1. Go to your Google Account
2. Navigate to Security > App passwords
3. Create a new app password for "Mail" and your application
4. Use this password in the MAIL_PASSWORD setting

## Testing

### Test Scripts

Two test scripts are provided in the `backend/tests` directory:

1. **test_email_config.py**: Verifies SMTP settings are working correctly

   ```
   python tests/test_email_config.py
   ```

2. **test_email_verification.py**: Tests the complete verification flow
   ```
   python tests/test_email_verification.py
   ```

### Development Testing Tool

For development, a test tool is available at `/test-verification` that allows developers to:

- Generate verification links without sending emails
- Test the verification flow without real email delivery

## Troubleshooting

### Common Issues

1. **Emails not sending**:

   - Check SMTP credentials in .env
   - Ensure Gmail "Less secure app access" is enabled or App Password is used
   - Check server logs for SMTP errors

2. **Verification link not working**:

   - Ensure FRONTEND_URL is correctly set
   - Check token expiration (default: 7 days)
   - Verify route configuration in frontend

3. **Verification not completing**:
   - Check backend logs for token validation errors
   - Ensure database connectivity is working
   - Check for any CORS issues

## Security Considerations

1. **Token Security**:

   - Tokens are randomly generated with sufficient entropy
   - Tokens have an expiration date
   - Tokens are single-use and invalidated after verification

2. **Email Security**:
   - SMTP uses TLS encryption
   - Email templates clearly identify the sender
   - No sensitive information is included in emails

## Future Improvements

Potential enhancements for the verification system:

1. Rate limiting to prevent email flooding
2. IP-based abuse detection
3. Backup verification methods (SMS, etc.)
4. Admin interface for monitoring verification status
5. Automated retry for failed email deliveries

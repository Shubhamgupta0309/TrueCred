# Email Configuration for TrueCred

This document explains how to configure email sending for the TrueCred application.

## Overview

TrueCred uses email for:

- Account verification
- Password reset
- Notifications about credential verifications

## Configuration

### 1. Environment Variables

Edit the `.env` file in the backend directory and set the following variables:

```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_DEFAULT_SENDER=TrueCred <noreply@truecred.com>
```

### 2. Using Gmail

If you're using Gmail as your email provider:

1. You'll need to create an "App Password" since Gmail doesn't allow direct SMTP access with your regular password
2. Go to your Google Account → Security → 2-Step Verification
3. At the bottom, click on "App passwords"
4. Select "Mail" and "Other (Custom name)"
5. Name it "TrueCred" and click "Generate"
6. Use the generated 16-character password as your `MAIL_PASSWORD`

### 3. Other Email Providers

For other providers, adjust the settings accordingly:

- **Outlook/Hotmail**:

  ```
  MAIL_SERVER=smtp-mail.outlook.com
  MAIL_PORT=587
  MAIL_USE_TLS=True
  ```

- **Yahoo**:
  ```
  MAIL_SERVER=smtp.mail.yahoo.com
  MAIL_PORT=587
  MAIL_USE_TLS=True
  ```

## Testing Email Configuration

To test if your email configuration is working:

1. Set up the environment variables as described above
2. Start the backend server
3. Register a new user
4. You should receive a verification email at the address you registered with

## Development Mode

In development mode, all emails are also logged to the console, so you can see their content even if email sending is not configured.

## Security Notes

- Never commit your email password to the repository
- Use environment variables for sensitive information
- Consider using a dedicated email account for your application

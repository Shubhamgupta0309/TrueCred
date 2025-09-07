# TrueCred Frontend Pages

This document lists all the pages that need to be implemented for the TrueCred frontend application.

## Authentication Pages

1. **Login Page** (`/login`)

   - User login form
   - OAuth options
   - Password reset link

2. **Registration Page** (`/register`)

   - User registration form
   - Terms of service agreement
   - Email verification notification

3. **Forgot Password Page** (`/forgot-password`)

   - Email input for password reset
   - Reset instructions

4. **Reset Password Page** (`/reset-password/:token`)

   - New password input
   - Password confirmation

5. **Email Verification Page** (`/verify-email/:token`)
   - Email verification confirmation

## User Dashboard

6. **Dashboard Home** (`/dashboard`)
   - Overview of credentials and experiences
   - Verification status summary
   - Recent activity feed
   - Quick action buttons

## Credential Management

7. **Credentials List** (`/credentials`)

   - List of all user credentials
   - Filter and sort options
   - Verification status indicators

8. **Add Credential** (`/credentials/add`)

   - Form to add a new credential
   - Document upload
   - Issuer information

9. **Edit Credential** (`/credentials/:id/edit`)

   - Form to edit an existing credential
   - Update documents

10. **Credential Details** (`/credentials/:id`)

    - Detailed view of a credential
    - Verification status
    - Blockchain verification info
    - Share options

11. **Credential Verification Request** (`/credentials/:id/request-verification`)
    - Form to request verification
    - Issuer selection
    - Additional proof submission

## Experience Management

12. **Experiences List** (`/experiences`)

    - List of all user experiences
    - Filter and sort options
    - Verification status indicators

13. **Add Experience** (`/experiences/add`)

    - Form to add a new experience
    - Link to credentials
    - Company/organization information

14. **Edit Experience** (`/experiences/:id/edit`)

    - Form to edit an existing experience

15. **Experience Details** (`/experiences/:id`)

    - Detailed view of an experience
    - Verification status
    - Associated credentials
    - Blockchain verification info

16. **Experience Verification Request** (`/experiences/:id/request-verification`)
    - Form to request verification
    - Verifier selection
    - Additional proof submission

## Verification Dashboard (for Issuers/Verifiers)

17. **Verification Requests** (`/verification/requests`)

    - List of pending verification requests
    - Filter by type (credential/experience)

18. **Verify Credential** (`/verification/credentials/:id`)

    - Credential details
    - Verification action buttons
    - Notes/feedback form

19. **Verify Experience** (`/verification/experiences/:id`)
    - Experience details
    - Verification action buttons
    - Notes/feedback form

## Blockchain Integration

20. **Blockchain Verification** (`/blockchain/verify/:type/:id`)

    - Verification status on blockchain
    - Transaction details
    - Timestamp information

21. **Credential Blockchain Preparation** (`/blockchain/credentials/:id/prepare`)

    - Preparation details
    - Confirmation screen

22. **Experience Blockchain Preparation** (`/blockchain/experiences/:id/prepare`)
    - Preparation details
    - Confirmation screen

## Profile and Settings

23. **User Profile** (`/profile`)

    - Personal information
    - Professional summary
    - Profile picture
    - Contact information

24. **Profile Settings** (`/settings/profile`)

    - Edit profile information
    - Privacy settings

25. **Account Settings** (`/settings/account`)

    - Change password
    - Email preferences
    - Delete account
    - Connected accounts

26. **Notification Settings** (`/settings/notifications`)
    - Email notification preferences
    - In-app notification settings

## Public Pages

27. **Landing Page** (`/`)

    - Introduction to TrueCred
    - Features overview
    - Call-to-action buttons

28. **About Page** (`/about`)

    - About TrueCred
    - Mission and vision
    - Team information

29. **Public Profile** (`/users/:username`)

    - Public view of user profile
    - Verified credentials and experiences
    - Contact options (if enabled)

30. **Credential Verification** (`/verify/:credential_id`)
    - Public verification page
    - Credential details
    - Blockchain verification status

## Admin Panel

31. **Admin Dashboard** (`/admin`)

    - System overview
    - User statistics
    - Verification statistics

32. **User Management** (`/admin/users`)

    - List of users
    - User actions (suspend, delete, etc.)
    - Role management

33. **Credential Management** (`/admin/credentials`)

    - List of all credentials
    - Filter and search options
    - Verification status management

34. **Experience Management** (`/admin/experiences`)

    - List of all experiences
    - Filter and search options
    - Verification status management

35. **System Settings** (`/admin/settings`)
    - Application settings
    - Blockchain configuration
    - Email templates

## Additional Pages

36. **Search Results** (`/search`)

    - Search results for users, credentials, and experiences
    - Filter options

37. **Help Center** (`/help`)

    - FAQ
    - User guides
    - Contact support

38. **Privacy Policy** (`/privacy`)

    - Privacy policy details

39. **Terms of Service** (`/terms`)

    - Terms of service details

40. **404 Page** (`/404`)

    - Not found page

41. **Error Page** (`/error`)
    - General error page

## Mobile-Specific Views

For responsive design and mobile app integration, all these pages should have mobile-optimized views that maintain the same functionality while adapting to smaller screen sizes.

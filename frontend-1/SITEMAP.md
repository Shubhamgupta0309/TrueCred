# TrueCred Frontend Site Map

```
├── Public Pages
│   ├── Landing Page (/)
│   ├── About Page (/about)
│   ├── Public Profile (/users/:username)
│   ├── Credential Verification (/verify/:credential_id)
│   ├── Privacy Policy (/privacy)
│   ├── Terms of Service (/terms)
│   └── Help Center (/help)
│
├── Authentication
│   ├── Login (/login)
│   ├── Register (/register)
│   ├── Forgot Password (/forgot-password)
│   ├── Reset Password (/reset-password/:token)
│   └── Email Verification (/verify-email/:token)
│
├── Dashboard
│   └── Dashboard Home (/dashboard)
│
├── Credentials
│   ├── Credentials List (/credentials)
│   ├── Add Credential (/credentials/add)
│   ├── Edit Credential (/credentials/:id/edit)
│   ├── Credential Details (/credentials/:id)
│   └── Request Verification (/credentials/:id/request-verification)
│
├── Experiences
│   ├── Experiences List (/experiences)
│   ├── Add Experience (/experiences/add)
│   ├── Edit Experience (/experiences/:id/edit)
│   ├── Experience Details (/experiences/:id)
│   └── Request Verification (/experiences/:id/request-verification)
│
├── Verification (for Issuers/Verifiers)
│   ├── Verification Requests (/verification/requests)
│   ├── Verify Credential (/verification/credentials/:id)
│   └── Verify Experience (/verification/experiences/:id)
│
├── Blockchain
│   ├── Blockchain Verification (/blockchain/verify/:type/:id)
│   ├── Credential Preparation (/blockchain/credentials/:id/prepare)
│   └── Experience Preparation (/blockchain/experiences/:id/prepare)
│
├── Profile & Settings
│   ├── User Profile (/profile)
│   ├── Profile Settings (/settings/profile)
│   ├── Account Settings (/settings/account)
│   └── Notification Settings (/settings/notifications)
│
├── Admin Panel
│   ├── Admin Dashboard (/admin)
│   ├── User Management (/admin/users)
│   ├── Credential Management (/admin/credentials)
│   ├── Experience Management (/admin/experiences)
│   └── System Settings (/admin/settings)
│
└── Utility Pages
    ├── Search Results (/search)
    ├── 404 Page (/404)
    └── Error Page (/error)
```

## Implementation Priority

### Phase 1: Core Functionality

1. Authentication pages
2. Dashboard home
3. Credentials management
4. Experiences management
5. User profile

### Phase 2: Verification System

1. Verification request pages
2. Verification dashboard
3. Blockchain integration pages

### Phase 3: Admin and Additional Features

1. Admin panel
2. Public pages
3. Help center
4. Settings pages

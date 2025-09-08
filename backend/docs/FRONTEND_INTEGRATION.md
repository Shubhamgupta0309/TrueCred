# Frontend-Backend Integration Guide

This document outlines how the TrueCred frontend and backend are connected and how to use the integration.

## Overview

The TrueCred application consists of:
- **Frontend**: React application using Vite
- **Backend**: Flask API with JWT authentication

## Integration Components

### 1. API Client

The frontend communicates with the backend using an Axios-based API client located at `frontend/src/services/api.js`. This client:

- Sets the base URL for all API requests
- Handles authentication token management
- Provides interceptors for token refresh on expiration
- Exposes service objects for different API areas (auth, credentials, experiences, etc.)

### 2. Authentication Context

React context at `frontend/src/context/AuthContext.jsx` provides:

- User authentication state management
- Login/logout functionality
- Token storage in localStorage
- User role information

### 3. CORS Configuration

The backend is configured to accept cross-origin requests from the frontend development servers at:
- http://localhost:3000 (React default)
- http://localhost:5173 (Vite default)

## Using the Integration

### In Frontend Components

```jsx
// Import the authentication hook
import { useAuth } from '../context/AuthContext';

// Import API services
import { credentialService } from '../services/api';

function MyComponent() {
  // Access auth state and methods
  const { user, isAuthenticated, login, logout } = useAuth();
  
  // Example API call
  const fetchCredentials = async () => {
    try {
      const response = await credentialService.getCredentials();
      console.log(response.data);
    } catch (error) {
      console.error('Error fetching credentials:', error);
    }
  };
  
  return (
    <div>
      {isAuthenticated ? (
        <>
          <p>Welcome, {user.username}!</p>
          <button onClick={fetchCredentials}>Get Credentials</button>
          <button onClick={logout}>Logout</button>
        </>
      ) : (
        <button onClick={() => login({ username: 'test', password: 'password' })}>
          Login
        </button>
      )}
    </div>
  );
}
```

### Starting the Development Environment

1. Start the backend:
```bash
cd backend
python app.py
```

2. Start the frontend:
```bash
cd frontend
npm run dev
```

## API Endpoints

The frontend API client is configured to work with these backend endpoints:

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/auth/logout` - User logout
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/connect-wallet` - Connect blockchain wallet

### Credentials
- `GET /api/credentials` - Get user credentials
- `POST /api/credentials/request` - Request a new credential
- `POST /api/credentials/{id}/verify` - Verify a credential

### Experiences
- `GET /api/experiences` - Get user experiences
- `POST /api/experiences/request` - Request a new experience record
- `POST /api/experiences/{id}/verify` - Verify an experience

### College Operations
- `GET /api/credentials/pending` - Get pending credential requests
- `POST /api/credentials/{id}/approve` - Approve a credential request
- `POST /api/credentials/{id}/reject` - Reject a credential request
- `GET /api/credentials/history` - Get verification history

### Company Operations
- `GET /api/experiences/pending` - Get pending experience requests
- `POST /api/experiences/{id}/approve` - Approve an experience request
- `POST /api/experiences/{id}/reject` - Reject an experience request
- `GET /api/experiences/history` - Get experience verification history

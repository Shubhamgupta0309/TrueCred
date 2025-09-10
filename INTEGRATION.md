# TrueCred Integration Guide

This guide provides instructions for connecting the frontend and backend components of the TrueCred application.

## Prerequisites

- Node.js (v16+ recommended)
- Python 3.8+
- MongoDB (local or Atlas)
- Git

## Project Structure

```
TrueCred/
├── frontend/             # React frontend
│   ├── src/              # Source code
│   ├── public/           # Static files
│   └── package.json      # Dependencies
├── backend/              # Flask backend
│   ├── app.py            # Main application
│   ├── models/           # Database models
│   ├── routes/           # API routes
│   ├── services/         # Business logic
│   ├── middleware/       # Request middleware
│   ├── utils/            # Utility functions
│   └── requirements.txt  # Dependencies
├── project-docs/         # Documentation
└── dev-start.ps1         # Development startup script
```

## Setup

### Backend Setup

1. **Create a virtual environment**:

   ```
   cd backend
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

2. **Install dependencies**:

   ```
   pip install -r requirements.txt
   ```

3. **Create a .env file in the backend directory**:

   ```
   SECRET_KEY=your-super-secret-key
   JWT_SECRET_KEY=your-jwt-secret-key-for-truecred
   MONGO_URI=mongodb+srv://truecred:truecred@cluster0.ozrvhec.mongodb.net/truecred?retryWrites=true&w=majority
   FLASK_ENV=development
   DEBUG=True
   ```

4. **Test MongoDB connection**:
   ```
   python tests/test_mongodb_connection.py
   ```

### Frontend Setup

1. **Install dependencies**:

   ```
   cd frontend
   npm install
   ```

2. **Create a .env file in the frontend directory**:
   ```
   VITE_API_BASE_URL=http://localhost:5000/api
   ```

## Running the Application

### Method 1: Using the Development Script

Run both frontend and backend with a single command:

```
.\dev-start.ps1
```

### Method 2: Manual Startup

1. **Start the backend**:

   ```
   cd backend
   .\venv\Scripts\activate  # Windows
   python app.py
   ```

2. **Start the frontend (in another terminal)**:
   ```
   cd frontend
   npm run dev
   ```

## Testing the API Connection

1. **Test user registration**:

   ```
   cd backend
   python tests/test_user_registration.py
   ```

2. **Test user login**:

   ```
   python tests/test_user_login.py
   ```

3. **Test CORS configuration**:
   ```
   python tests/test_cors.py
   ```

## Troubleshooting

### MongoDB Connection Issues

- Ensure MongoDB is running (if local)
- Verify MongoDB Atlas credentials and network access
- Check the MongoDB connection string in the `.env` file

### CORS Issues

- Make sure the frontend origin is allowed in the backend CORS configuration
- Check for any network or proxy issues

### Authentication Issues

- Verify JWT token is being properly sent in the Authorization header
- Check token expiration settings

## Next Steps

1. Implement the remaining frontend components for credential management
2. Connect to the blockchain smart contracts
3. Implement IPFS for document storage
4. Add user profile and verification flow

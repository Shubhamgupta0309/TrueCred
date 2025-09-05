# TrueCred Backend

This is the backend API for the TrueCred application, a blockchain-based credential verification system.

## Technology Stack

- **Flask**: Web framework
- **MongoDB Atlas**: Cloud database
- **PyMongo**: MongoDB ODM for Python
- **JWT**: Authentication
- **Web3.py**: Blockchain interaction
- **IPFS**: Decentralized document storage

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- MongoDB Atlas account (or local MongoDB installation)
- Ethereum node or provider (Infura, Ganache, etc.)
- IPFS node (optional for development)

### Environment Setup

1. Clone the repository:

   ```
   git clone https://github.com/yourusername/TrueCred.git
   cd TrueCred/backend
   ```

2. Create a virtual environment:

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

   If you encounter any issues with MongoDB, install PyMongo directly:

   ```
   pip install pymongo[srv] python-dotenv
   ```

4. Create a `.env` file based on the template:
   ```
   cp .env.sample .env
   ```

5. Edit the `.env` file with your actual credentials:
   ```
   FLASK_APP=app.py
   FLASK_ENV=development
   MONGO_URI=mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/truecred?retryWrites=true&w=majority
   JWT_SECRET_KEY=your_secret_key
   WEB3_PROVIDER_URI=http://127.0.0.1:8545  # or your Infura endpoint
   IPFS_HOST=127.0.0.1
   IPFS_PORT=5001
   ```

   > ⚠️ **SECURITY WARNING**: Never commit your `.env` file with real credentials to Git. The `.env` file is included in `.gitignore` to prevent accidental commits.

### MongoDB Atlas Setup

1. Create a MongoDB Atlas account at [https://www.mongodb.com/cloud/atlas/register](https://www.mongodb.com/cloud/atlas/register)
2. Create a new cluster (the free tier is sufficient for development)
3. Set up database access (create a username and password)
4. Configure network access (allow access from your IP address)
5. Get your connection string from the "Connect" button on your cluster
6. Replace the placeholders in the connection string with your username and password
7. Test your connection:
   ```
   python scripts/test_mongodb_connection.py
   ```

### Running the Application

1. Start the Flask server:

   ```
   flask run
   ```

2. The API will be available at `http://127.0.0.1:5000/`.

## API Endpoints

- **Authentication**

  - `POST /api/auth/register`: Register a new user
  - `POST /api/auth/login`: Login and get an access token
  - `GET /api/auth/profile`: Get user profile

- **Credentials**

  - `GET /api/credentials/`: Get all credentials for the current user
  - `POST /api/credentials/`: Create a new credential
  - `GET /api/credentials/<id>`: Get a specific credential
  - `POST /api/credentials/<id>/verify`: Verify a credential

- **Experiences**

  - `GET /api/experiences/`: Get all experiences for the current user
  - `POST /api/experiences/`: Create a new experience
  - `GET /api/experiences/<id>`: Get a specific experience
  - `PUT /api/experiences/<id>`: Update an experience

- **Health**
  - `GET /api/health/`: Check system health and dependencies

## Development

### Project Structure

```
backend/
├── app.py                # Main application entry point
├── config.py             # Configuration settings
├── requirements.txt      # Dependencies
├── contracts/            # Ethereum smart contracts
├── models/               # Database models
├── routes/               # API routes
├── services/             # Business logic
├── utils/                # Utility functions
├── middleware/           # Custom middleware
└── tests/                # Test cases
```

### Testing

Run tests with pytest:

```
pytest
```

## Deployment

For production deployment:

1. Update the `.env` file with production settings
2. Set `FLASK_ENV=production`
3. Use a production WSGI server like Gunicorn:
   ```
   gunicorn -w 4 'app:create_app()'
   ```

## License

[MIT License](LICENSE)

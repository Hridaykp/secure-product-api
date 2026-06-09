# FastAPI Product Management API

A FastAPI-based REST API for managing products and users with JWT-based authentication, built with MongoDB for data persistence.

## Features

- **User Authentication**: User registration and login with JWT token-based authentication
- **Protected Endpoints**: Access user profile with valid JWT token
- **Product Management**: Create, read, update, and delete products
- **Price Filtering**: Filter products by price ranges from external API
- **Data Validation**: Pydantic-based request validation
- **Secure Password Storage**: bcrypt-based password hashing
- **MongoDB Integration**: Persistent data storage with MongoDB
- **OAuth2 Security**: OAuth2PasswordBearer implementation for token-based authentication

## Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: MongoDB
- **Authentication**: JWT (JSON Web Tokens) with OAuth2
- **Password Security**: bcrypt via passlib
- **API Documentation**: Automatic OpenAPI/Swagger UI
- **External API Integration**: requests library for price filtering

## Prerequisites

- Python 3.7+
- MongoDB running locally on `mongodb://localhost:27017`
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Hridaykp/FastApi.git
cd FastApi
```

2. Install dependencies:
```bash
pip install fastapi uvicorn pymongo pydantic python-jose passlib bcrypt requests
```

3. Ensure MongoDB is running:
```bash
# On macOS with Homebrew
brew services start mongodb-community

# Or run with Docker
docker run -d -p 27017:27017 mongo
```

## Running the Application

Start the FastAPI server:
```bash
uvicorn api:app --reload
```

The API will be available at `http://localhost:8000`

- **API Documentation**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative Docs**: `http://localhost:8000/redoc` (ReDoc)

## API Endpoints

### Authentication Endpoints
- `POST /register` - Register a new user
  - **Body**: `{ "username": "string", "password": "string" }`
  - **Response**: User registration success message
  - **Error**: Returns 400 if username already exists

- `POST /login` - Login user and get JWT access token
  - **Body**: OAuth2 form data with username and password
  - **Response**: `{ "access_token": "string", "token_type": "bearer" }`
  - **Error**: Returns 400 for invalid credentials
  - **Token Expiration**: 30 minutes (configurable via ACCESS_TOKEN_EXPIRE_MINUTES)

- `GET /profile` - Get current user profile (requires valid JWT token)
  - **Headers**: `Authorization: Bearer <token>`
  - **Response**: `{ "id": "string", "username": "string" }`
  - **Error**: Returns 401 if token is invalid or missing

### General Endpoints
- `GET /` - Home page
- `GET /about` - About page

### Product Endpoints
- `GET /products` - Fetch all products from MongoDB
  - **Response**: List of all products with serialized data
  
- `GET /products/id/{id}` - Fetch product by MongoDB ObjectId
  - **Parameters**: `id` (MongoDB ObjectId as string)
  - **Response**: Product details if found
  - **Error**: Returns 400 for invalid ObjectId format
  
- `GET /products/price/{price}` - Filter products by price range
  - **Parameters**: `price` (integer)
  - **Response**: Products with price in range [price, price+1) from external API
  - **Note**: Uses fakestoreapi.com for data

- `POST /products` - Add new product to MongoDB
  - **Body**: `{ "name": "string", "price": float }`
  - **Response**: `{ "message": "string", "id": "string", "product": {...} }`

- `PUT /products/{prod_id}` - Update existing product
  - **Parameters**: `prod_id` (MongoDB ObjectId as string)
  - **Body**: `{ "name": "string", "price": float }`
  - **Response**: Success message
  - **Error**: Returns 404 if product not found

- `DELETE /products/{prod_id}` - Delete product by ID
  - **Parameters**: `prod_id` (MongoDB ObjectId as string)
  - **Response**: Success or "not found" message

## Database Schema

### Users Collection
```json
{
  "_id": "ObjectId",
  "username": "string",
  "password": "string (bcrypt hashed)"
}
```

### Products Collection
```json
{
  "_id": "ObjectId",
  "name": "string",
  "price": "float"
}
```

## Authentication Flow

1. **User Registration**: POST to `/register` with username and password
2. **Password Hashing**: Passwords are hashed using bcrypt before storage
3. **User Login**: POST to `/login` to receive JWT access token (30 minutes expiration)
4. **Token Usage**: Include token in Authorization header as `Bearer <token>`
5. **Token Validation**: Tokens are decoded and verified for protected endpoints

## Configuration

The following configurations can be modified in `api.py`:

```python
SECRET_KEY = "your-super-secret-key"  # Change this to a secure random key
ALGORITHM = "HS256"                    # JWT algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = 30       # Token expiration time
mongo_uri = "mongodb://localhost:27017"  # MongoDB connection URI
```

## Contributing

Feel free to fork this repository and submit pull requests for any improvements.

## License

This project is open source and available under the MIT License.

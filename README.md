# Secure Product API

A comprehensive FastAPI-based REST API for managing products and users with JWT-based authentication, role-based access control (RBAC), and MongoDB for data persistence.

## Features

- **User Authentication**: User registration and login with JWT token-based authentication
- **Token Management**: Access and refresh token functionality with automatic expiration
- **Role-Based Access Control (RBAC)**: User and Admin roles with permission management
- **Protected Endpoints**: Role-specific access control for user profiles and admin operations
- **Product Management**: Create, read, update, and delete products
- **Price Filtering**: Filter products by price ranges from external API (fakestoreapi.com)
- **Admin Dashboard**: Statistics and user management capabilities
- **Data Validation**: Pydantic-based request validation
- **Secure Password Storage**: bcrypt-based password hashing
- **MongoDB Integration**: Persistent data storage with MongoDB
- **OAuth2 Security**: OAuth2PasswordBearer implementation for token-based authentication
- **CORS Support**: Cross-Origin Resource Sharing enabled for all origins

## Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Server**: Uvicorn
- **Database**: MongoDB
- **Authentication**: JWT (JSON Web Tokens) with OAuth2
- **Password Security**: bcrypt via passlib
- **API Documentation**: Automatic OpenAPI/Swagger UI
- **External API Integration**: requests library for price filtering
- **Environment Management**: python-dotenv

## Project Structure

```
secure-product-api/
├── main.py                 # Main FastAPI application entry point
├── requirements.txt        # Python dependencies
├── core/
│   ├── config.py          # Configuration constants (SECRET_KEY, ALGORITHM, token expiration)
│   └── security.py        # Security utilities (password hashing, JWT token creation)
├── routers/
│   ├── auth.py            # Authentication endpoints (register, login, refresh token)
│   ├── products.py        # Product management endpoints (CRUD operations)
│   └── admin.py           # Admin operations (user promotion, dashboard statistics)
├── database/
│   └── connection.py      # MongoDB connection and collection definitions
└── schemas/
    ├── user.py            # User request/response schemas
    └── product.py         # Product request/response schemas
```

## Prerequisites

- Python 3.7+
- MongoDB running locally on `mongodb://localhost:27017`
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Hridaykp/secure-product-api.git
cd secure-product-api
```

2. Install dependencies:
```bash
pip install -r requirements.txt
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
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

- **API Documentation**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative Docs**: `http://localhost:8000/redoc` (ReDoc)

## API Endpoints

### General Endpoints
- `GET /` - Home page
- `GET /about` - About page

### Authentication Endpoints

- **`POST /register`** - Register a new user
  - **Body**: `{ "username": "string", "password": "string" }`
  - **Response**: `{ "message": "User registered successfully !!" }`
  - **Error**: Returns 400 if username already exists

- **`POST /login`** - Login user and get JWT tokens
  - **Body**: OAuth2 form data with username and password
  - **Response**: `{ "access_token": "string", "refresh_token": "string", "token_type": "bearer" }`
  - **Error**: Returns 400 for invalid credentials
  - **Token Expiration**: Access token valid for 30 minutes, refresh token for 15 days

- **`POST /refresh-token`** - Refresh access token using refresh token
  - **Body**: `{ "refresh_token": "string" }`
  - **Response**: `{ "access_token": "string", "token_type": "bearer" }`
  - **Error**: Returns 401 if refresh token is invalid

- **`GET /profile`** - Get current user profile (requires valid JWT token)
  - **Headers**: `Authorization: Bearer <access_token>`
  - **Response**: `{ "id": "string", "username": "string", "role": "string" }`
  - **Error**: Returns 401 if token is invalid or missing
  - **Access**: Available to "user" and "admin" roles

### Product Endpoints

- **`GET /products`** - Fetch all products from MongoDB
  - **Response**: `{ "message": "products are here", "products": [...] }`

- **`GET /products/id/{id}`** - Fetch product by MongoDB ObjectId
  - **Parameters**: `id` (MongoDB ObjectId as string)
  - **Response**: `{ "product": {...}, "message": "product fetched successfully" }`
  - **Error**: Returns 400 for invalid ObjectId format, 404 if not found

- **`GET /products/price/{price}`** - Filter products by price range
  - **Parameters**: `price` (integer)
  - **Response**: Products with price in range [price, price+1) from fakestoreapi.com

- **`POST /products`** - Add new product to MongoDB
  - **Body**: `{ "name": "string", "price": float }`
  - **Response**: `{ "message": "product created successfully", "id": "string", "product": {...} }`

- **`PUT /products/{prod_id}`** - Update existing product
  - **Parameters**: `prod_id` (MongoDB ObjectId as string)
  - **Body**: `{ "name": "string", "price": float }`
  - **Response**: `{ "message": "product updated successfully !!" }`
  - **Error**: Returns 400 for invalid ObjectId format, 404 if not found

- **`DELETE /products/{prod_id}`** - Delete product by ID
  - **Parameters**: `prod_id` (MongoDB ObjectId as string)
  - **Response**: `{ "message": "Product deleted successfully" }`
  - **Error**: Returns 400 for invalid ObjectId format, 404 if not found

### Admin Endpoints

- **`POST /admin/make-admin/{username}`** - Promote a user to admin role
  - **Parameters**: `username` (string)
  - **Headers**: `Authorization: Bearer <admin_access_token>`
  - **Response**: `{ "message": "{username} is now admin" }`
  - **Error**: Returns 404 if user not found, 403 if not authorized
  - **Access**: Admin role required

- **`GET /admin/dashboard`** - Get admin dashboard with statistics
  - **Headers**: `Authorization: Bearer <admin_access_token>`
  - **Response**: 
    ```json
    {
      "message": "Welcome to the admin dashboard !!",
      "current_admin": "admin_username",
      "statistics": {
        "total_users": integer,
        "total_admins": integer
      }
    }
    ```
  - **Error**: Returns 403 if not authorized
  - **Access**: Admin role required

## Database Schema

### Users Collection
```json
{
  "_id": "ObjectId",
  "username": "string",
  "password": "string (bcrypt hashed)",
  "role": "string (user | admin)"
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
3. **User Login**: POST to `/login` to receive JWT access and refresh tokens
4. **Token Usage**: Include access token in Authorization header as `Bearer <token>`
5. **Token Validation**: Tokens are decoded and verified for protected endpoints
6. **Token Refresh**: Use refresh token at `/refresh-token` to get new access token without re-login

## Role-Based Access Control (RBAC)

The API implements two user roles:

- **user**: Default role assigned to all new users. Can access their own profile and use product endpoints.
- **admin**: Elevated role with access to admin operations. Can promote other users to admin and view dashboard statistics.

## Configuration

The following configurations can be modified in `core/config.py`:

```python
SECRET_KEY = "your-super-secret-key"       # Change this to a secure random key
ALGORITHM = "HS256"                        # JWT algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = 30           # Access token expiration time
REFRESH_TOKEN_EXPIRE_DAYS = 15             # Refresh token expiration time
```

Also ensure MongoDB URI is correctly configured in `database/connection.py`:
```python
mongo_uri = "mongodb://localhost:27017"
```

## Contributing

Feel free to fork this repository and submit pull requests for any improvements.

## License

This project is open source and available under the MIT License.

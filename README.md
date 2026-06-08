# FastAPI Product Management API

A FastAPI-based REST API for managing products and users with authentication, built with MongoDB for data persistence.

## Features

- **User Authentication**: User registration and login with JWT token-based authentication
- **Product Management**: Create, read, update, and delete products
- **Price Filtering**: Filter products by price ranges
- **Data Validation**: Pydantic-based request validation
- **Secure Password Storage**: bcrypt-based password hashing
- **MongoDB Integration**: Persistent data storage with MongoDB

## Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: MongoDB
- **Authentication**: JWT (JSON Web Tokens) with OAuth2
- **Password Security**: bcrypt via passlib
- **API Documentation**: Automatic OpenAPI/Swagger UI

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

### Authentication
- `POST /register` - Register a new user
  - **Body**: `{ "username": "string", "password": "string" }`
  - **Response**: User registration success message

- `POST /login` - Login user and get JWT token
  - **Body**: `{ "username": "string", "password": "string" }`
  - **Response**: JWT access token

### Products
- `GET /` - Home page
- `GET /about` - About page
- `GET /products` - Fetch all products
- `GET /products/id/{id}` - Fetch product by MongoDB ObjectId
- `GET /products/price/{price}` - Filter products by price range
- `POST /products` - Add new product
  - **Body**: `{ "name": "string", "price": float }`
- `PUT /products/{prod_id}` - Update product
  - **Body**: `{ "name": "string", "price": float }`
- `DELETE /products/{prod_id}` - Delete product

## Database Schema

### Users Collection
```json
{
  "_id": "ObjectId",
  "username": "string",
  "password": "string (hashed)"
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

## Security Notes

- ⚠️ **Update SECRET_KEY**: Replace `"your-super-secret-key"` in `api.py` with a strong, unique secret key
- Uses bcrypt for secure password hashing
- JWT tokens expire after 30 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)

## Example Usage

```bash
# Register a new user
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "secret123"}'

# Add a product
curl -X POST "http://localhost:8000/products" \
  -H "Content-Type: application/json" \
  -d '{"name": "Laptop", "price": 999.99}'

# Get all products
curl -X GET "http://localhost:8000/products"

# Get product by ID
curl -X GET "http://localhost:8000/products/id/507f1f77bcf86cd799439011"

# Filter by price
curl -X GET "http://localhost:8000/products/price/500"
```

## Contributing

Feel free to fork this repository and submit pull requests for any improvements.

## License

This project is open source and available under the MIT License.

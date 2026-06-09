"""
Configuration settings for the FastAPI application
"""
from datetime import timedelta

# MongoDB Configuration
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "fastapi_db"
PRODUCTS_COLLECTION = "products"
USERS_COLLECTION = "users"

# JWT Configuration
SECRET_KEY = "your-super-secret-key"  # Change this to a secure random key in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
PASSWORD_HASH_SCHEME = "bcrypt"

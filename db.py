"""
Database client and connection management
"""
from pymongo import MongoClient
from config import MONGO_URI, DB_NAME, PRODUCTS_COLLECTION, USERS_COLLECTION


class Database:
    """MongoDB database connection manager"""
    
    _client = None
    _db = None
    _products_collection = None
    _users_collection = None
    
    @classmethod
    def connect(cls):
        """Initialize MongoDB connection"""
        if cls._client is None:
            cls._client = MongoClient(MONGO_URI)
            cls._db = cls._client[DB_NAME]
            cls._products_collection = cls._db[PRODUCTS_COLLECTION]
            cls._users_collection = cls._db[USERS_COLLECTION]
    
    @classmethod
    def get_db(cls):
        """Get database instance"""
        if cls._db is None:
            cls.connect()
        return cls._db
    
    @classmethod
    def get_products_collection(cls):
        """Get products collection"""
        if cls._products_collection is None:
            cls.connect()
        return cls._products_collection
    
    @classmethod
    def get_users_collection(cls):
        """Get users collection"""
        if cls._users_collection is None:
            cls.connect()
        return cls._users_collection
    
    @classmethod
    def close(cls):
        """Close database connection"""
        if cls._client is not None:
            cls._client.close()
            cls._client = None
            cls._db = None
            cls._products_collection = None
            cls._users_collection = None

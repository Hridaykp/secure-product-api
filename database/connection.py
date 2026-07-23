from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017"

client = MongoClient(MONGO_URI)
db = client["fastapi_db"]




products_collection = db["products"]
users_collection = db["users"]
tokens_collection = db["tokens"]

# Check the connection and print the list of collections in the database
# print("Connected to MongoDB successfully !!", db.list_collection_names()) 
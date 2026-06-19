from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017"

client = MongoClient(MONGO_URI)
db = client["fastapi_db"]

# print("Connected to MongoDB successfully !!")
# Collections
products_collection = db["products"]
users_collection = db["users"]
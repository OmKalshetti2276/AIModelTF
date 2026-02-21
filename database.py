from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI not found in environment variables")

client = MongoClient(MONGO_URI)

db = client["smart_irrigation"]

predictions_collection = db["predictions"]

print("MongoDB Connected Successfully")
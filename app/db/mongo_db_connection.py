from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection details
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "fastapi_auth")

# MongoDB client instance
client = None
db = None

async def connect_to_mongodb():
    """Connect to MongoDB at application startup"""
    global client, db
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    print(f"Connected to MongoDB at {MONGODB_URL}")

async def close_mongodb_connection():
    """Close MongoDB connection at application shutdown"""
    global client
    if client:
        client.close()
        print("MongoDB connection closed")

def get_database():
    """Get database instance"""
    return db
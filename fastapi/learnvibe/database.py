#new one
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

# Hardcoded password (URL encode it to handle special characters)
MONGODB_PASSWORD = "bhavaniprasad"
MONGODB_PASSWORD_ENCODED = quote_plus(MONGODB_PASSWORD)
MONGODB_URL = f"mongodb+srv://kolaprasad001:{MONGODB_PASSWORD_ENCODED}@roadmap.xe1hzql.mongodb.net/?retryWrites=true&w=majority&appName=roadmap"

client = MongoClient(MONGODB_URL)
database = client.get_database("learnvibe")

# Collections
user_registration_collection = database["user_registration"]
users_profile_collection = database["users_profile"]
password_reset_collection = database["password_reset_codes"]
contact_collection = database["contact_submissions"]

def init_db():
    """Initialize database indexes"""
    try:
        # User registration indexes
        user_registration_collection.create_index("email", unique=True)
        
        # Student profile indexes
        users_profile_collection.create_index("studentId", unique=True)
        users_profile_collection.create_index("email")
        
        # Password reset indexes with TTL (1 hour expiry)
        password_reset_collection.create_index("created_at", expireAfterSeconds=3600)
        password_reset_collection.create_index("email")
        
        # Contact form indexes
        contact_collection.create_index("email")
        contact_collection.create_index("created_at")
        
        print("Database indexes created successfully")
    except Exception as e:
        print(f"Error creating indexes: {e}")
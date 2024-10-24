#database_module.py

import os
from pymongo import MongoClient
from dotenv import load_dotenv
import io
from PIL import Image
import gridfs  # MongoDB GridFS for large file storage (optional)
import cv2

# Load environment variables from .env file
load_dotenv()

# Get the MongoDB connection string from environment variables
MONGO_URI = os.getenv("MONGO_URI")

# Initialize MongoDB connection
client = MongoClient(MONGO_URI)
db = client['SchemeDetectionDatabase']  # Replace with your actual database name

# Define collection (replace with actual collection name)
collection = db['schemes']

# Function to retrieve an element by name
def get_element_by_name(name):
    try:
        return collection.find_one({"name": name})
    except Exception as e:
        print(f"Error retrieving element: {e}")
        return None


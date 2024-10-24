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


# Function to insert a detected element
def insert_detected_element(element_data):
    try:
        collection.insert_one(element_data)
        print(f"Inserted element: {element_data['name']}")
    except Exception as e:
        print(f"Error inserting element: {e}")


# Function to retrieve detected elements
def get_all_elements():
    try:
        return list(collection.find())
    except Exception as e:
        print(f"Error retrieving elements: {e}")
        return []


def get_element_by_name(name):
    try:
        # Change the query to look for image_name instead of name
        result = collection.find_one({"image_name": name})
        print(f"Database query result for '{name}': {result}")  # Debug print
        return result
    except Exception as e:
        print(f"Error retrieving element: {e}")
        return None

# Function to store image metadata (or the image if using GridFS)
def store_image(image_data, image_name):
    try:
        # Convert OpenCV BGR image to RGB and then to PIL image
        image_rgb = cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(image_rgb)
        
        # Convert the image to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')  # Save image as PNG
        img_byte_arr = img_byte_arr.getvalue()

        # Store the image in MongoDB
        collection.insert_one({"image_name": image_name, "image_data": img_byte_arr})
        print(f"Inserted image: {image_name}")
    except Exception as e:
        print(f"Error storing image: {e}")

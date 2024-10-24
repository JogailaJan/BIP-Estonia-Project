#database_module.py

import os
from pymongo import MongoClient
from dotenv import load_dotenv
import io
from PIL import Image
import cv2
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Get the MongoDB connection string from environment variables
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable is not set")

try:
    # Initialize MongoDB connection
    client = MongoClient(MONGO_URI)
    # Test the connection
    client.admin.command('ping')
    db = client['SchemeDetectionDatabase']
    collection = db['schemes']
    logger.info("Successfully connected to MongoDB")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    raise

def store_image(image_data, image_name):
    """
    Store an image in MongoDB with improved error handling and validation.
    
    Args:
        image_data: numpy array containing the image data
        image_name: str, name to identify the image
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Input validation
        if image_data is None:
            logger.error("No image data provided")
            return False
            
        if not isinstance(image_name, str) or not image_name.strip():
            logger.error("Invalid image name provided")
            return False

        # Check if image name already exists
        existing_image = collection.find_one({"image_name": image_name})
        if existing_image:
            logger.warning(f"Image with name '{image_name}' already exists")
            return False

        # Convert OpenCV BGR image to RGB and then to PIL image
        image_rgb = cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(image_rgb)
        
        # Convert the image to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        # Store the image in MongoDB
        result = collection.insert_one({
            "image_name": image_name,
            "image_data": img_byte_arr
        })
        
        if result.inserted_id:
            logger.info(f"Successfully stored image: {image_name}")
            return True
        else:
            logger.error("Failed to insert image into database")
            return False

    except cv2.error as e:
        logger.error(f"OpenCV error while processing image: {e}")
        return False
    except Exception as e:
        logger.error(f"Error storing image: {e}")
        return False

def get_element_by_name(name):
    """
    Retrieve an element from MongoDB by name with improved error handling.
    
    Args:
        name: str, name of the element to retrieve
    
    Returns:
        dict or None: The element if found, None otherwise
    """
    try:
        if not isinstance(name, str) or not name.strip():
            logger.error("Invalid name provided")
            return None

        result = collection.find_one({"image_name": name})
        if result:
            logger.info(f"Successfully retrieved element: {name}")
            return result
        else:
            logger.warning(f"No element found with name: {name}")
            return None

    except Exception as e:
        logger.error(f"Error retrieving element: {e}")
        return None

def get_all_elements():
    """
    Retrieve all elements from MongoDB with improved error handling.
    
    Returns:
        list: List of elements, empty list if error occurs
    """
    try:
        elements = list(collection.find())
        logger.info(f"Successfully retrieved {len(elements)} elements")
        return elements
    except Exception as e:
        logger.error(f"Error retrieving elements: {e}")
        return []
from pymongo import MongoClient
from PIL import Image
import io
import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
# MongoDB connection details
client = MongoClient(MONGO_URI)
db = client['SchemeDetectionDatabase']  # Replace with your actual database name
collection = db['schemes']

# Fetch the image data
scheme_name = "test3"  # Replace with your image's scheme name
scheme_data = collection.find_one({"image_name": scheme_name})

if scheme_data and "image_data" in scheme_data:
    # Convert the binary data to an image
    image_data = scheme_data["image_data"]
    img = Image.open(io.BytesIO(image_data))

    # Optionally, display it using OpenCV (converted to numpy array)
    img_np = np.array(img)
    img_cv = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    cv2.imshow("Loaded Image", img_cv)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("Image not found in the database.")

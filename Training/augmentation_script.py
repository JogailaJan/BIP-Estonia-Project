import cv2
import numpy as np
from PIL import Image
import random
import os

def augment_image(image_path, output_dir, num_versions=50):
    # Load the image
    img = Image.open(image_path)

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for i in range(num_versions):
        # Convert PIL image to NumPy array
        img_np = np.array(img)

        # Randomly choose augmentations
        augmented_img = img_np

        # Random rotation
        angle = random.uniform(-45, 45)
        augmented_img = Image.fromarray(augmented_img)
        augmented_img = augmented_img.rotate(angle)

        # Random resizing
        scale_factor = random.uniform(0.5, 1.5)
        width, height = augmented_img.size
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        augmented_img = augmented_img.resize((new_width, new_height))

        # Random skew
        skew_factor = random.uniform(-0.3, 0.3)
        skew_matrix = (1, skew_factor, 0, 0, 1, skew_factor)
        augmented_img = augmented_img.transform(augmented_img.size, Image.AFFINE, skew_matrix)

        # Convert back to NumPy for OpenCV blurring
        augmented_img_np = np.array(augmented_img)

        # Random blur
        if random.random() > 0.5:
            blur_value = random.choice([3, 5, 7])  # Choose from kernel sizes
            augmented_img_np = cv2.GaussianBlur(augmented_img_np, (blur_value, blur_value), 0)

        # Save the augmented image
        output_filename = f"augmented_{i}.png"
        output_filepath = os.path.join(output_dir, output_filename)
        cv2.imwrite(output_filepath, augmented_img_np)

    print(f"{num_versions} augmented images saved to {output_dir}")

def augment_all_symbols(symbols_dir, output_base_dir, num_versions_per_symbol=50):
    # List all symbol images in the original images folder
    for filename in os.listdir(symbols_dir):
        if filename.endswith(".png"):
            symbol_name = os.path.splitext(filename)[0]
            image_path = os.path.join(symbols_dir, filename)
            output_dir = os.path.join(output_base_dir, symbol_name)

            # Augment the image
            augment_image(image_path, output_dir, num_versions=num_versions_per_symbol)

# Example usage
symbols_dir = "Training/original_images"  # Path to the folder containing the original symbol images
output_base_dir = "Training/augmented_images"  # Directory to save augmented images
augment_all_symbols(symbols_dir, output_base_dir, num_versions_per_symbol=50)

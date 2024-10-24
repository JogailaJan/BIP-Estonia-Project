# camera_module.py

import cv2  # OpenCV library for computer vision tasks, used here for camera access and image processing
import threading  # Library for running tasks in parallel threads, allowing the camera to run in the background
import time  # Standard library used to add delays (sleep) in the camera loop
from PIL import Image, ImageTk, ImageDraw, ImageFont  # PIL (Python Imaging Library) used to process images and display them in Tkinter
import tkinter as tk  # Tkinter is a standard Python library for creating graphical user interfaces (GUIs)
import io
from database_module import get_element_by_name
from tkinter import messagebox
import numpy as np
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def confidence_to_color(confidence):
    """
    Map a confidence level (0 to 1) to a color ranging from red to green.
    """
    # Ensure confidence is between 0 and 1
    confidence = max(0, min(1, confidence))

    
    if confidence <= 0.25:
        # Interpolate between red and orange (0 to 25% confidence)
        return interpolate_color((255, 0, 0), (255, 165, 0), confidence / 0.25)
    elif confidence <= 0.50:
        # Interpolate between orange and yellow (25% to 50% confidence)
        return interpolate_color((255, 165, 0), (255, 255, 0), (confidence - 0.25) / 0.25)
    elif confidence <= 0.75:
        # Interpolate between yellow and green (50% to 75% confidence)
        return interpolate_color((255, 255, 0), (0, 255, 0), (confidence - 0.50) / 0.25)
    else:
        # Green for high confidence (75% to 100%)
        return (0, 255, 0)
        
def interpolate_color(color1, color2, factor):
    """
    Linearly interpolate between two RGB colors by a given factor (0 to 1).
    """
    return tuple(int(color1[i] + (color2[i] - color1[i]) * factor) for i in range(3))


# The CameraModule class manages the camera feed, displaying it in a GUI, and allows interaction with highlighted areas
class CameraModule:
    def __init__(self, parent_frame, ui_module):
        self.ui_module = ui_module
        self.live_mode = True
        self.camera_label = tk.Label(parent_frame)
        self.camera_label.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        self.camera_label.bind("<Button-1>", self.on_camera_click)
        
        self.current_frame = None
        self.loaded_image = None
        self.running = True
        
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            logger.error("Cannot open camera")
            self.running = False
        else:
            logger.info("Camera opened successfully")
            self.camera_thread = threading.Thread(target=self.camera_loop)
            self.camera_thread.daemon = True
            self.camera_thread.start()
            self.update_gui_frame()

    # Function to handle mouse clicks on the camera feed
    def on_camera_click(self, event):
        """Handle click on the live camera feed to detect if a highlight is clicked and change the color."""
        click_x, click_y = event.x, event.y  # Get the position of the click within the label

        # Get the size of the label (where the camera feed is displayed)
        label_width = self.camera_label.winfo_width()
        label_height = self.camera_label.winfo_height()

        # Get the dimensions of the original camera frame (this may not be available if the camera hasn't started)
        if self.current_frame is not None:
            frame_height, frame_width = self.current_frame.shape[:2]
        else:
            frame_height, frame_width = 480, 640  # Default values if no frame is available

        # Calculate the size of the resized frame within the label
        frame_aspect_ratio = frame_width / frame_height
        label_aspect_ratio = label_width / label_height

        if label_aspect_ratio > frame_aspect_ratio:
            # If the label is wider than the frame, adjust the frame size based on the label's height
            new_height = label_height
            new_width = int(new_height * frame_aspect_ratio)
        else:
            # If the label is taller than the frame, adjust the frame size based on the label's width
            new_width = label_width
            new_height = int(new_width / frame_aspect_ratio)

        # Calculate any offsets (if the frame doesn't fill the label completely)
        offset_x = (label_width - new_width) // 2
        offset_y = (label_height - new_height) // 2

        # Adjust the click coordinates to account for the frame's position within the label
        adjusted_click_x = click_x - offset_x
        adjusted_click_y = click_y - offset_y

        # Check if the click falls inside the actual image area
        if 0 <= adjusted_click_x < new_width and 0 <= adjusted_click_y < new_height:
            # Map the click position from the resized frame back to the original camera frame
            frame_x = adjusted_click_x * frame_width / new_width
            frame_y = adjusted_click_y * frame_height / new_height

            # Check if the click falls inside any of the highlighted areas
            for highlight in self.ui_module.element_manager.highlights:
                x1, y1, x2, y2 = highlight['coords']  # Get the coordinates of the highlight
                if x1 <= frame_x <= x2 and y1 <= frame_y <= y2:  # Check if the click is within this highlight
                    # Use the unique 'id' to select the highlight and sync with TreeView
                    self.ui_module.element_manager.select_highlight(highlight['id'])  # Select highlight using unique ID
                    self.ui_module.treeview_module.select_treeview_item_by_id(highlight['id'])  # Sync TreeView selection
                    break  # Stop checking after finding the clicked highlight
        else:
            # If the click is outside the image area, do nothing
            pass

    def get_current_frame(self):
        """
        Get the current frame being displayed, whether it's from the camera or a loaded image.
        
        Returns:
            numpy.ndarray: The current frame in BGR format, or None if no frame is available
        """
        try:
            if self.current_frame is None:
                logger.warning("No frame available")
                return None
                
            # If we're displaying a loaded image
            if not self.live_mode and self.loaded_image is not None:
                logger.debug("Returning loaded image frame")
                # Convert PIL Image to BGR numpy array
                return cv2.cvtColor(np.array(self.loaded_image), cv2.COLOR_RGB2BGR)
            
            # If we're in live mode
            if self.live_mode and self.current_frame is not None:
                logger.debug("Returning live camera frame")
                return self.current_frame.copy()
                
            logger.warning("No valid frame available")
            return None
            
        except Exception as e:
            logger.error(f"Error getting current frame: {e}")
            return None

    def camera_loop(self):
        """Capture frames from the camera when live_mode is True."""
        while self.running:
            if self.live_mode:
                try:
                    ret, frame = self.cap.read()
                    if ret:
                        self.current_frame = frame.copy()
                    else:
                        logger.error("Failed to read from camera")
                        self.running = False
                except Exception as e:
                    logger.error(f"Error in camera loop: {e}")
                    self.running = False
            time.sleep(0.03)

    def update_gui_frame(self):
        """Update the GUI with either camera feed or loaded image."""
        if not self.live_mode and self.loaded_image is not None:
            # Display loaded image
            self.display_loaded_image()
        elif self.live_mode and self.current_frame is not None:
            # Display camera feed
            self.display_camera_frame()
            
        # Schedule next update
        self.ui_module.root.after(30, self.update_gui_frame)

    def display_camera_frame(self):
        """Display the current camera frame with highlights."""
        frame = self.current_frame.copy()
        frame_height, frame_width = frame.shape[:2]
        frame_aspect_ratio = frame_width / frame_height

        label_width = self.camera_label.winfo_width()
        label_height = self.camera_label.winfo_height()

        if label_width > 0 and label_height > 0:
            label_aspect_ratio = label_width / label_height

            if label_aspect_ratio > frame_aspect_ratio:
                new_height = label_height
                new_width = int(new_height * frame_aspect_ratio)
            else:
                new_width = label_width
                new_height = int(new_width / frame_aspect_ratio)

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img = img.resize((new_width, new_height))
            self.draw_highlights(img, frame_width, frame_height, new_width, new_height)
            
            imgtk = ImageTk.PhotoImage(image=img)
            self.camera_label.imgtk = imgtk
            self.camera_label.configure(image=imgtk)

    def display_loaded_image(self):
        """Display the loaded image with highlights."""
        if self.loaded_image:
            label_width = self.camera_label.winfo_width()
            label_height = self.camera_label.winfo_height()
            
            if label_width > 0 and label_height > 0:
                img_width, img_height = self.loaded_image.size
                img_aspect_ratio = img_width / img_height
                label_aspect_ratio = label_width / label_height

                if label_aspect_ratio > img_aspect_ratio:
                    new_height = label_height
                    new_width = int(new_height * img_aspect_ratio)
                else:
                    new_width = label_width
                    new_height = int(new_width / img_aspect_ratio)

                img = self.loaded_image.resize((new_width, new_height))
                self.draw_highlights(img, img_width, img_height, new_width, new_height)
                
                imgtk = ImageTk.PhotoImage(image=img)
                self.camera_label.imgtk = imgtk
                self.camera_label.configure(image=imgtk)

    def draw_highlights(self, img, orig_width, orig_height, new_width, new_height):
        """Draw highlights on the image."""
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except IOError:
            font = ImageFont.load_default()

        for highlight in self.ui_module.element_manager.highlights:
            element_id = highlight['id']
            element_name = ""
            confidence = 0.0

            for category, elements in self.ui_module.element_manager.detected_elements.items():
                for element in elements:
                    if element['id'] == element_id:
                        element_name = element['name']
                        confidence = float(element['details'].get('Confidence', 0))

            confidence_percentage = confidence if confidence <= 1 else confidence / 100

            if highlight['selected']:
                color_rgb = (0, 255, 255)
            else:
                color_rgb = confidence_to_color(confidence_percentage)

            color = f'#{color_rgb[0]:02x}{color_rgb[1]:02x}{color_rgb[2]:02x}'

            scaled_coords = [
                int(highlight['coords'][0] * new_width / orig_width),
                int(highlight['coords'][1] * new_height / orig_height),
                int(highlight['coords'][2] * new_width / orig_width),
                int(highlight['coords'][3] * new_height / orig_height),
            ]
            
            draw.rectangle(scaled_coords, outline=color, width=2)
            text_position = (scaled_coords[0], scaled_coords[1] - 20)
            display_text = f"{element_name} ({confidence:.2f})"
            draw.text(text_position, display_text, fill=color, font=font)

    def load_image_from_database(self, scheme_name):
        """Load a scheme from the database and display it instead of the live camera feed."""
        try:
            print(f"Looking for scheme: '{scheme_name}'")
            scheme_data = get_element_by_name(scheme_name)
            
            if not scheme_data:
                print(f"No scheme data found for '{scheme_name}'")
                return False
                
            if "image_data" not in scheme_data:
                print(f"No image data found in scheme '{scheme_name}'")
                return False
                
            image_data = scheme_data["image_data"]
            
            # Convert binary data to PIL Image
            self.loaded_image = Image.open(io.BytesIO(image_data))
            self.live_mode = False  # Stop camera feed
            
            # Convert PIL Image to numpy array for compatibility with existing code
            frame_array = cv2.cvtColor(np.array(self.loaded_image), cv2.COLOR_RGB2BGR)
            self.current_frame = frame_array
            
            print(f"Successfully loaded scheme '{scheme_name}'")
            messagebox.showinfo("Success", f"Scheme '{scheme_name}' loaded successfully!")
            return True
            
        except Exception as e:
            print(f"Error loading scheme '{scheme_name}': {e}")
            return False

    def reset_to_live_detection(self):
        """Reset the camera feed to live detection mode."""
        self.loaded_image = None  # Clear loaded image
        self.live_mode = True  # Turn on live mode

    def release_resources(self):
        """Cleanup method to properly release camera resources."""
        try:
            self.running = False
            if hasattr(self, 'camera_thread'):
                self.camera_thread.join()
            if hasattr(self, 'cap'):
                self.cap.release()
            logger.info("Camera resources released")
        except Exception as e:
            logger.error(f"Error releasing camera resources: {e}")

    def __del__(self):
        self.release_resources()
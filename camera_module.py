# camera_module.py

import cv2  # OpenCV library for computer vision tasks, used here for camera access and image processing
import threading  # Library for running tasks in parallel threads, allowing the camera to run in the background
import time  # Standard library used to add delays (sleep) in the camera loop
from PIL import Image, ImageTk, ImageDraw, ImageFont  # PIL (Python Imaging Library) used to process images and display them in Tkinter
import tkinter as tk  # Tkinter is a standard Python library for creating graphical user interfaces (GUIs)

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
        self.ui_module = ui_module  # Reference to another part of the program (ui_module), which manages GUI and highlights

        # Create a label widget in the Tkinter window to display the camera feed
        self.camera_label = tk.Label(parent_frame)
        self.camera_label.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)  # Make the label fill the available space

        # Bind mouse click events to a custom function (self.on_camera_click) that will handle clicks on the camera feed
        self.camera_label.bind("<Button-1>", self.on_camera_click)

        self.current_frame = None  # Will hold the current frame captured from the camera
        self.running = True  # A flag to keep the camera running in the background

        # Initialize the camera using OpenCV (0 is the default camera on the system)
        self.cap = cv2.VideoCapture(0)  # OpenCV's method to access the camera
        if not self.cap.isOpened():  # Check if the camera opened successfully
            print("Cannot open camera")  # Print an error if the camera cannot be accessed
            self.running = False  # Stop further processing if no camera is available
        else:
            print("Camera opened successfully")  # Indicate that the camera opened correctly
            # Start a background thread to capture frames from the camera
            self.camera_thread = threading.Thread(target=self.camera_loop)
            self.camera_thread.daemon = True  # Mark the thread as a daemon, so it closes when the main program exits
            self.camera_thread.start()  # Start the camera thread

            # Start updating the GUI to display the frames captured from the camera
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

    # Function running in a separate thread to continuously capture frames from the camera
    def camera_loop(self):
        while self.running:  # Keep looping while the camera is running
            ret, frame = self.cap.read()  # Read a frame from the camera (ret is a success flag, frame is the actual image)
            if ret:  # If the frame was captured successfully
                self.current_frame = frame.copy()  # Make a copy of the frame (to avoid altering the original data)
            else:
                print("Failed to read from camera")  # Print an error if the frame capture fails
                self.running = False  # Stop the camera loop if there's a failure
            time.sleep(0.03)  # Pause for a brief moment (30 milliseconds) to avoid overloading the system


    def update_gui_frame(self):
        if self.current_frame is not None:  # If there is a valid frame to display
            frame = self.current_frame.copy()  # Make a copy of the frame for further processing
            frame_height, frame_width = frame.shape[:2]  # Get the frame's dimensions (height and width)
            frame_aspect_ratio = frame_width / frame_height  # Calculate the aspect ratio of the frame

            # Get the dimensions of the label in the GUI (this is where the camera feed is displayed)
            label_width = self.camera_label.winfo_width()
            label_height = self.camera_label.winfo_height()

            # Make sure the label dimensions are valid (non-zero) before proceeding
            if label_width > 0 and label_height > 0:
                label_aspect_ratio = label_width / label_height  # Calculate the aspect ratio of the label

                # Determine the best size for the frame, scaling it to fit inside the label while maintaining the aspect ratio
                if label_aspect_ratio > frame_aspect_ratio:
                    new_height = label_height  # Use the full height of the label
                    new_width = int(new_height * frame_aspect_ratio)  # Calculate the width that maintains the aspect ratio
                else:
                    new_width = label_width  # Use the full width of the label
                    new_height = int(new_width / frame_aspect_ratio)

                # Convert the OpenCV BGR frame (Blue-Green-Red color format) to RGB format for displaying with Tkinter
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)  # Convert the frame into a PIL image
                img = img.resize((new_width, new_height))  # Resize the image to fit the label dimensions
                draw = ImageDraw.Draw(img)  # Create an object for drawing on the image

                # Try to load a custom font (arial.ttf), or use a default font if the custom font isn't available
                try:
                    font = ImageFont.truetype("arial.ttf", 16)
                except IOError:
                    font = ImageFont.load_default()

                # Loop through the highlights (regions of interest) to draw them on the camera feed
                for highlight in self.ui_module.element_manager.highlights:
                    element_id = highlight['id']
                    element_name = ""
                    confidence = 0.0

                    # Get the element details including confidence score
                    for category, elements in self.ui_module.element_manager.detected_elements.items():
                        for element in elements:
                            if element['id'] == element_id:
                                element_name = element['name']
                                confidence = float(element['details'].get('Confidence', 0))  # Get confidence score

                    # Normalize confidence (0-1)
                    confidence_percentage = confidence if confidence <= 1 else confidence / 100

                    # Set color based on whether the element is selected
                    if highlight['selected']:
                        # Bright cyan for selected element
                        color_rgb = (0, 255, 255)  # Cyan
                    else:
                        # Color based on confidence level
                        color_rgb = confidence_to_color(confidence_percentage)

                    # Convert RGB to hex for drawing
                    color = f'#{color_rgb[0]:02x}{color_rgb[1]:02x}{color_rgb[2]:02x}'  # Convert RGB to hex

                    # Scale the highlight coordinates to match the resized image
                    scaled_coords = [
                        int(highlight['coords'][0] * new_width / frame_width),
                        int(highlight['coords'][1] * new_height / frame_height),
                        int(highlight['coords'][2] * new_width / frame_width),
                        int(highlight['coords'][3] * new_height / frame_height),
                    ]
                    draw.rectangle(scaled_coords, outline=color, width=2)  # Draw a rectangle around the highlighted area

                    # Position the text label slightly above the highlighted area with confidence level
                    text_position = (scaled_coords[0], scaled_coords[1] - 20)
                    display_text = f"{element_name} ({confidence:.2f})"  # Name + Confidence
                    draw.text(text_position, display_text, fill=color, font=font)  # Draw the name with confidence

                # Convert the PIL image back to a format that Tkinter can display
                imgtk = ImageTk.PhotoImage(image=img)
                self.camera_label.imgtk = imgtk  # Store the image reference to prevent it from being garbage collected
                self.camera_label.configure(image=imgtk)  # Update the label with the new image

        # Schedule this function to run again after 30 milliseconds to create a smooth update loop
        self.ui_module.root.after(30, self.update_gui_frame)


    # Function to stop the camera and clean up resources
    def release_resources(self):
        # Stop the camera loop by setting the running flag to False
        self.running = False
        if hasattr(self, 'camera_thread'):  # If the camera thread exists
            self.camera_thread.join()  # Wait for the camera thread to finish
        # Release the camera resource (close the connection to the camera)
        if self.cap and self.cap.isOpened():
            self.cap.release()
        print("Camera resources released")  # Confirm that the resources have been released

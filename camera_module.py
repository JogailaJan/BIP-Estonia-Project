import cv2
import threading
import time
from PIL import Image, ImageTk, ImageDraw, ImageFont
import tkinter as tk

class CameraModule:
    def __init__(self, parent_frame, ui_module):
        self.ui_module = ui_module

        self.camera_label = tk.Label(parent_frame)
        self.camera_label.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        self.camera_label.bind("<Button-1>", self.on_camera_click)

        self.current_frame = None
        self.running = True

        # Initialize the camera
        self.cap = cv2.VideoCapture(0)  # Removed CAP_DSHOW to test if the issue is flag-related
        if not self.cap.isOpened():
            print("Cannot open camera")
            self.running = False
        else:
            print("Camera opened successfully")
            # Start the camera thread
            self.camera_thread = threading.Thread(target=self.camera_loop)
            self.camera_thread.daemon = True
            self.camera_thread.start()

            # Start updating the GUI with frames
            self.update_gui_frame()

    def camera_loop(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                self.current_frame = frame.copy()  # Use a copy of the frame
            else:
                print("Failed to read from camera")
                self.running = False
            time.sleep(0.01)

    def update_gui_frame(self):
        if self.current_frame is not None:
            frame = self.current_frame.copy()
            frame_height, frame_width = frame.shape[:2]
            frame_aspect_ratio = frame_width / frame_height

            # Calculate new dimensions for the frame that fit the available space while maintaining aspect ratio
            label_width = self.camera_label.winfo_width()
            label_height = self.camera_label.winfo_height()

            # Ensure the label width and height are valid (non-zero)
            if label_width > 0 and label_height > 0:
                label_aspect_ratio = label_width / label_height

                # Determine the best-fit dimensions that maintain the aspect ratio
                if label_aspect_ratio > frame_aspect_ratio:
                    new_height = label_height
                    new_width = int(new_height * frame_aspect_ratio)
                else:
                    new_width = label_width
                    new_height = int(new_width / frame_aspect_ratio)

                # Resize the frame with the new dimensions while maintaining aspect ratio
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                img = img.resize((new_width, new_height))
                draw = ImageDraw.Draw(img)

                # Font for the element names
                try:
                    font = ImageFont.truetype("arial.ttf", 16)
                except IOError:
                    font = ImageFont.load_default()

                # Draw the highlights and names on the camera feed
                for highlight in self.ui_module.element_manager.highlights:
                    color = "#FF5733" if highlight['selected'] else "#3380FF"

                    # Scale highlight coordinates based on the new image dimensions
                    scaled_coords = [
                        int(highlight['coords'][0] * new_width / frame_width),
                        int(highlight['coords'][1] * new_height / frame_height),
                        int(highlight['coords'][2] * new_width / frame_width),
                        int(highlight['coords'][3] * new_height / frame_height),
                    ]
                    draw.rectangle(scaled_coords, outline=color, width=2)

                    # Position the text above the top-left corner of the highlight
                    text_position = (scaled_coords[0], scaled_coords[1] - 20)
                    draw.text(text_position, highlight['name'], fill=color, font=font)

                # Convert to Tkinter-compatible image
                imgtk = ImageTk.PhotoImage(image=img)
                self.camera_label.imgtk = imgtk
                self.camera_label.configure(image=imgtk)

        # Schedule the next GUI frame update
        self.ui_module.root.after(10, self.update_gui_frame)

    def on_camera_click(self, event):
        """Handle click on the live camera feed to detect if a highlight is clicked and change the color."""
        click_x, click_y = event.x, event.y

        # Get the current size of the camera label
        label_width = self.camera_label.winfo_width()
        label_height = self.camera_label.winfo_height()

        # Get original frame dimensions
        if self.current_frame is not None:
            frame_height, frame_width = self.current_frame.shape[:2]
        else:
            frame_height, frame_width = 480, 640  # Default values if frame not available

        # Calculate new dimensions for the frame that fit the available space while maintaining aspect ratio
        frame_aspect_ratio = frame_width / frame_height
        label_aspect_ratio = label_width / label_height

        if label_aspect_ratio > frame_aspect_ratio:
            # The label is wider than the frame
            new_height = label_height
            new_width = int(new_height * frame_aspect_ratio)
        else:
            # The label is taller than the frame
            new_width = label_width
            new_height = int(new_width / frame_aspect_ratio)

        # Calculate offsets (if any)
        offset_x = (label_width - new_width) // 2
        offset_y = (label_height - new_height) // 2

        # Adjust click positions
        adjusted_click_x = click_x - offset_x
        adjusted_click_y = click_y - offset_y

        # Check if click is within the image area
        if 0 <= adjusted_click_x < new_width and 0 <= adjusted_click_y < new_height:
            # Map click coordinates back to frame coordinates
            frame_x = adjusted_click_x * frame_width / new_width
            frame_y = adjusted_click_y * frame_height / new_height

            # Now check if the click is inside any highlight
            for highlight in self.ui_module.element_manager.highlights:
                x1, y1, x2, y2 = highlight['coords']
                if x1 <= frame_x <= x2 and y1 <= frame_y <= y2:
                    # Highlight clicked, mark it as selected and update information
                    self.ui_module.element_manager.select_highlight(highlight['name'])
                    break  # No need to check other highlights
        else:
            # Click was outside the image area
            pass

    def release_resources(self):
        # Stop the camera loop
        self.running = False
        if hasattr(self, 'camera_thread'):
            self.camera_thread.join()
        # Release the camera
        if self.cap and self.cap.isOpened():
            self.cap.release()
        print("Camera resources released")

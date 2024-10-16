# ui_module.py

import tkinter as tk
from tkinter import ttk, Label, Frame
from PIL import Image, ImageTk, ImageDraw, ImageFont
import json
import cv2
from categories_data import categories_info  # Import the categories data

class UIModule:
    def __init__(self, root):
        # In-memory storage for detected elements and their info
        self.detected_elements = {}
        self.selected_highlight = None  # To track the selected highlight

        # Create the main frames for the 3 sections with relative percentages and min-widths
        self.left_frame = Frame(root, bg="lightgrey")
        self.middle_frame = Frame(root, bg="white")
        self.right_frame = Frame(root, bg="lightgrey")

        # Add frames to the grid and configure weight and minsize for percentage-based layout
        self.left_frame.grid(row=0, column=0, sticky="nswe")
        self.middle_frame.grid(row=0, column=1, sticky="nswe")
        self.right_frame.grid(row=0, column=2, sticky="nswe")

        # Configure grid for window resizing
        root.grid_columnconfigure(0, weight=1, minsize=200)  # Section 1: 20% width, minimum 200px
        root.grid_columnconfigure(1, weight=3, minsize=400)  # Section 2: 60% width, minimum 400px
        root.grid_columnconfigure(2, weight=1, minsize=200)  # Section 3: 20% width, minimum 200px

        root.grid_rowconfigure(0, weight=1)  # Ensure the middle frame stretches properly

        # Initialize TreeView for the detected elements in Section 1
        self.category_tree = ttk.Treeview(self.left_frame)
        self.category_tree.heading("#0", text="Detected Elements", anchor="w")
        self.category_tree.pack(fill="both", expand=True)

        # Bind selection event in TreeView to display element info and change highlight color
        self.category_tree.bind("<<TreeviewSelect>>", self.update_element_info_from_list)

        # Initialize the camera feed and label in Section 2
        self.camera_label = Label(self.middle_frame)
        self.camera_label.pack(expand=True, fill="both")  # Fill the middle frame both horizontally and vertically
        self.camera_label.bind("<Button-1>", self.on_camera_click)  # Mouse click event

        # Initialize the information panel in Section 3
        self.info_label = Label(self.right_frame, text="Element Information", font=("Arial", 14))
        self.info_label.pack(pady=10)
        self.element_info = Label(self.right_frame, text="", font=("Arial", 12), bg="white", width=40, height=10, anchor="nw", justify="left")
        self.element_info.pack(pady=10)

        # Store detected elements highlights (bounding boxes)
        self.highlights = []

        # Start camera feed
        self.show_camera_feed()

    def show_camera_feed(self):
        cap = cv2.VideoCapture(0)

        def update_frame():
            ret, frame = cap.read()
            if ret:
                # Get original frame dimensions
                frame_height, frame_width = frame.shape[:2]
                frame_aspect_ratio = frame_width / frame_height

                # Calculate new dimensions for the frame that fit the available space while maintaining aspect ratio
                label_width = self.middle_frame.winfo_width()
                label_height = self.middle_frame.winfo_height()

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
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame)
                    img = img.resize((new_width, new_height))
                    draw = ImageDraw.Draw(img)

                    # Font for the element names
                    try:
                        font = ImageFont.truetype("arial.ttf", 16)  # Load font if available
                    except IOError:
                        font = ImageFont.load_default()  # Use default if arial.ttf is not available

                    # Draw the highlights and names on the camera feed
                    for highlight in self.highlights:
                        color = "red" if highlight['selected'] else "blue"

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

            # Call update_frame again after a delay to simulate real-time updates
            self.camera_label.after(10, update_frame)

        # Wait for the window to be fully initialized and sized before updating the frame
        self.camera_label.after(200, update_frame)

    def update_detected_elements(self, element_data):
        """
        Add elements detected by the detection module, including their associated information and highlight coordinates.
        element_data is a dictionary with keys: 'name', 'details', 'highlight_coordinates'.
        """
        name = element_data['name']
        details = element_data['details']
        highlight_coords = element_data['highlight_coordinates']

        # Find the category for this element
        category = None
        for cat, elements in categories_info.items():
            if name in elements:
                category = cat
                break
        if category is None:
            category = 'Unknown'

        stored_element_data = {
            'name': name,
            'details': details
        }

        if category not in self.detected_elements:
            self.detected_elements[category] = []
        self.detected_elements[category].append(stored_element_data)

        # Add highlight (bounding box) coordinates
        self.highlights.append({
            'coords': highlight_coords,
            'name': name,
            'selected': False  # Initially not selected
        })

        self.populate_treeview()

    def populate_treeview(self):
        """Update the TreeView dynamically with the current detected elements."""
        self.category_tree.delete(*self.category_tree.get_children())
        for category, elements in self.detected_elements.items():
            category_node = self.category_tree.insert("", "end", text=category, open=True)
            for element_data in elements:
                self.category_tree.insert(category_node, "end", text=element_data['name'])

    def update_element_info_from_list(self, event):
        """Display information and change the highlight color when an element is selected from the TreeView (Section 1)."""
        selected_item = self.category_tree.focus()
        item_text = self.category_tree.item(selected_item, 'text')

        # Find the element's detailed info in the detected elements data
        for category, elements in self.detected_elements.items():
            for element_data in elements:
                if element_data['name'] == item_text:
                    # Build the details string
                    details_str = '\n'.join(f"{key}: {value}" for key, value in element_data['details'].items())
                    # Display the element's information in Section 3
                    element_info_text = f"Name: {element_data['name']}\nCategory: {category}\nDetails:\n{details_str}"
                    self.element_info.config(text=element_info_text)

                    # Change the color of the corresponding highlight
                    for highlight in self.highlights:
                        highlight['selected'] = (highlight['name'] == item_text)

    def on_camera_click(self, event):
        """Handle click on the live camera feed to detect if a highlight is clicked and change the color."""
        click_x, click_y = event.x, event.y

        # Get the current size of the camera label
        label_width = self.camera_label.winfo_width()
        label_height = self.camera_label.winfo_height()

        # Get original frame dimensions
        frame_height, frame_width = 480, 640  # Assuming a 640x480 frame size for the camera

        # Adjust the click position according to the resized camera feed
        for highlight in self.highlights:
            x1, y1, x2, y2 = highlight['coords']
            scaled_x1 = int(x1 * label_width / frame_width)
            scaled_y1 = int(y1 * label_height / frame_height)
            scaled_x2 = int(x2 * label_width / frame_width)
            scaled_y2 = int(y2 * label_height / frame_height)

            if scaled_x1 <= click_x <= scaled_x2 and scaled_y1 <= click_y <= scaled_y2:
                # Highlight clicked, mark it as selected and update information in Section 3
                self.select_highlight(highlight['name'])

    def select_highlight(self, name):
        """Select a highlight by name, change its color, and display its info."""
        for highlight in self.highlights:
            highlight['selected'] = (highlight['name'] == name)

        # Find and display the info for the selected highlight
        for category, elements in self.detected_elements.items():
            for element_data in elements:
                if element_data['name'] == name:
                    # Build the details string
                    details_str = '\n'.join(f"{key}: {value}" for key, value in element_data['details'].items())
                    # Display the element's information in Section 3
                    element_info_text = f"Name: {element_data['name']}\nCategory: {category}\nDetails:\n{details_str}"
                    self.element_info.config(text=element_info_text)

        # Programmatically select the corresponding element in the TreeView (Section 1)
        self.select_treeview_item(name)

    def select_treeview_item(self, name):
        """Programmatically select the corresponding item in the TreeView (Section 1)."""
        for item in self.category_tree.get_children():
            for subitem in self.category_tree.get_children(item):
                if self.category_tree.item(subitem, 'text') == name:
                    # Select the item and focus on it in the TreeView
                    self.category_tree.selection_set(subitem)
                    self.category_tree.focus(subitem)
                    return

    def save_elements_to_json(self, file_path):
        """Save the detected elements and their information to a JSON file."""
        with open(file_path, 'w') as f:
            json.dump(self.detected_elements, f)

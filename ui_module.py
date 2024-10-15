# ui_module.py

import tkinter as tk
from tkinter import ttk, Label, Frame
from PIL import Image, ImageTk, ImageDraw, ImageFont
import json
import cv2

class UIModule:
    def __init__(self, root):
        # In-memory storage for detected elements and their info
        self.detected_elements = {}
        self.selected_highlight = None  # To track the selected highlight

        # Create the main frames for the 3 sections
        self.left_frame = Frame(root, width=300, height=800, bg="lightgrey")
        self.left_frame.grid(row=0, column=0, sticky="ns")

        self.middle_frame = Frame(root, width=600, height=800, bg="white")
        self.middle_frame.grid(row=0, column=1, sticky="ns")

        self.right_frame = Frame(root, width=300, height=800, bg="lightgrey")
        self.right_frame.grid(row=0, column=2, sticky="ns")

        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=2)
        root.grid_columnconfigure(2, weight=1)

        # Initialize TreeView for the detected elements
        self.category_tree = ttk.Treeview(self.left_frame)
        self.category_tree.heading("#0", text="Detected Elements", anchor="w")
        self.category_tree.pack(fill="both", expand=True)

        # Bind selection event in TreeView to display element info and change highlight color
        self.category_tree.bind("<<TreeviewSelect>>", self.update_element_info_from_list)

        # Initialize the camera feed and label
        self.camera_label = Label(self.middle_frame)
        self.camera_label.pack()
        self.camera_label.bind("<Button-1>", self.on_camera_click)  # Mouse click event

        # Initialize the information panel
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
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                draw = ImageDraw.Draw(img)

                # Font for the element names
                try:
                    font = ImageFont.truetype("arial.ttf", 16)  # Load font if available
                except IOError:
                    font = ImageFont.load_default()  # Use default if arial.ttf is not available

                # Draw the highlights and names on the camera feed
                for highlight in self.highlights:
                    color = "red" if highlight['selected'] else "blue"
                    draw.rectangle(highlight['coords'], outline=color, width=2)

                    # Get the top-left corner of the bounding box to position the name
                    x1, y1, x2, y2 = highlight['coords']
                    text_position = (x1, y1 - 20)  # Position the text above the highlight

                    # Draw the element name near the top-left corner of the highlight
                    draw.text(text_position, highlight['name'], fill=color, font=font)

                # Convert to Tkinter-compatible image
                img = img.resize((600, 400))  
                imgtk = ImageTk.PhotoImage(image=img)

                self.camera_label.imgtk = imgtk
                self.camera_label.configure(image=imgtk)

            # Call update_frame again after a delay to simulate real-time updates
            self.camera_label.after(10, update_frame)

        update_frame()

    def update_detected_elements(self, category, element_data, highlight_coords=None):
        """
        Add elements detected by the detection module, including their associated information and highlight coordinates.
        element_data is a dictionary with keys like 'name', 'type', 'details'.
        highlight_coords: Tuple with bounding box coordinates (x1, y1, x2, y2).
        """
        if category not in self.detected_elements:
            self.detected_elements[category] = []
        self.detected_elements[category].append(element_data)

        # Add highlight (bounding box) coordinates if provided
        if highlight_coords:
            self.highlights.append({
                'coords': highlight_coords,
                'name': element_data['name'],
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
                    # Display the element's information in Section 3
                    element_info_text = f"Name: {element_data['name']}\nType: {element_data['type']}\nDetails: {element_data['details']}"
                    self.element_info.config(text=element_info_text)

                    # Change the color of the corresponding highlight
                    for highlight in self.highlights:
                        highlight['selected'] = (highlight['name'] == item_text)

    def on_camera_click(self, event):
        """Handle click on the live camera feed to detect if a highlight is clicked and change the color."""
        click_x, click_y = event.x, event.y

        # Check if the click was inside any of the highlight bounding boxes
        for highlight in self.highlights:
            x1, y1, x2, y2 = highlight['coords']
            if x1 <= click_x <= x2 and y1 <= click_y <= y2:
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
                    element_info_text = f"Name: {element_data['name']}\nType: {element_data['type']}\nDetails: {element_data['details']}"
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

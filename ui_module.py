# ui_module.py

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk, ImageDraw, ImageFont
import json
import cv2
from categories_data import categories_info
import threading
import time
import os

class UIModule:
    def __init__(self, root):
        self.root = root

        # In-memory storage for detected elements and their info
        self.detected_elements = {}
        self.selected_highlight = None  # To track the selected highlight
        self.current_frame = None  # To store the current frame from the camera
        self.running = True  # Flag to control the camera thread

        # Get the style for accessing theme colors
        self.style = ttk.Style()

        # Create the main frames using ttkbootstrap Frames
        self.left_frame = ttk.Frame(root)
        self.middle_frame = ttk.Frame(root)
        self.right_frame = ttk.Frame(root)

        # Add frames to the grid and configure weight and minsize for percentage-based layout
        self.left_frame.grid(row=0, column=0, sticky=NSEW)
        self.middle_frame.grid(row=0, column=1, sticky=NSEW)
        self.right_frame.grid(row=0, column=2, sticky=NSEW)

        # Configure grid for window resizing
        root.grid_columnconfigure(0, weight=1, minsize=200)
        root.grid_columnconfigure(1, weight=3, minsize=400)
        root.grid_columnconfigure(2, weight=1, minsize=200)
        root.grid_rowconfigure(0, weight=1)

        # Customize the Treeview style
        style = ttk.Style()

        # Calculate the required row height based on the font size
        font_size_category = 13  # Adjusted for better fit
        font_size_element = 12
        # Assuming approximately 1.5 times the font size for row height
        max_row_height = int(max(font_size_category, font_size_element) * 1.6)

        style.configure("Custom.Treeview",
                        background=self.style.colors.bg,
                        foreground=self.style.colors.fg,
                        fieldbackground=self.style.colors.bg,
                        bordercolor=self.style.colors.border,
                        font=("Helvetica", font_size_element),
                        rowheight=max_row_height,
                        highlightthickness=0,
                        bd=0,
                        borderwidth=0)

        style.map('Custom.Treeview', background=[('selected', self.style.colors.selectbg)])

        # Remove the blue border by adjusting the style
        style.layout("Custom.Treeview", [('Custom.Treeview.treearea', {'sticky': 'nswe'})])

        # Initialize TreeView for the detected elements in Section 1
        self.category_tree = ttk.Treeview(
            self.left_frame,
            bootstyle="info",
            style="Custom.Treeview",
            selectmode="browse",
            show="tree"
        )
        self.category_tree.heading("#0", text="Detected Elements", anchor="w")
        self.category_tree.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Bind selection event in TreeView to display element info and change highlight color
        self.category_tree.bind("<<TreeviewSelect>>", self.update_element_info_from_list)

        # Initialize the camera feed and label in Section 2
        self.camera_label = tk.Label(self.middle_frame)
        self.camera_label.pack(expand=True, fill=BOTH, padx=10, pady=10)
        self.camera_label.bind("<Button-1>", self.on_camera_click)

        # Initialize the information panel in Section 3
        self.info_label = ttk.Label(
            self.right_frame,
            text="Element Information",
            font=("Helvetica", 16, "bold"),
            foreground="white"
        )
        self.info_label.pack(pady=(20, 10))

        # Configure colors for the Text widget to match the dark theme
        text_field_background = self.style.colors.inputbg
        text_field_foreground = self.style.colors.inputfg

        # Initialize the element_info Text widget
        self.element_info = tk.Text(
            self.right_frame,
            font=("Helvetica", 12),
            width=40,
            height=15,
            bg=text_field_background,
            fg=text_field_foreground,
            insertbackground=text_field_foreground,
            relief="flat"
        )
        self.element_info.pack(pady=(0, 20), padx=10)
        self.element_info.config(state='disabled')

        # Store detected elements highlights (bounding boxes)
        self.highlights = []

        # Initialize the camera
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            print("Cannot open camera")
            self.running = False
        else:
            # Start the camera thread
            self.camera_thread = threading.Thread(target=self.camera_loop)
            self.camera_thread.daemon = True  # Daemonize thread
            self.camera_thread.start()

            # Start updating the GUI with frames
            self.update_gui_frame()

    def camera_loop(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                self.current_frame = frame
            else:
                print("Failed to read from camera")
                self.running = False
            time.sleep(0.01)  # Slight delay to prevent high CPU usage

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
                for highlight in self.highlights:
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
        self.root.after(10, self.update_gui_frame)

    def update_detected_elements_list(self, detected_elements):
        """
        Update the detected elements list without clearing it entirely.
        Only add new elements and remove missing ones.
        """
        # Convert current detected elements to a set of names for easy comparison
        current_elements = set()
        for category in self.detected_elements:
            for element in self.detected_elements[category]:
                current_elements.add((category, element['name']))

        # Convert new detected elements to a set of names
        new_elements = set()
        for element_data in detected_elements:
            name = element_data['name']
            # Find the category
            category = None
            for cat, elements in categories_info.items():
                if name in elements:
                    category = cat
                    break
            if category is None:
                category = 'Unknown'
            new_elements.add((category, name))

        # Find elements to add and remove
        elements_to_add = new_elements - current_elements
        elements_to_remove = current_elements - new_elements

        # Remove elements that are no longer detected
        for category, element_name in elements_to_remove:
            self.remove_detected_element(category, element_name)

        # Add new detected elements
        for element_data in detected_elements:
            name = element_data['name']
            # Find the category
            category = None
            for cat, elements in categories_info.items():
                if name in elements:
                    category = cat
                    break
            if category is None:
                category = 'Unknown'
            if (category, name) in elements_to_add:
                self.update_detected_elements(element_data)
            else:
                # Update highlight coordinates if element already exists
                for highlight in self.highlights:
                    if highlight['name'] == element_data['name']:
                        highlight['coords'] = element_data['highlight_coordinates']
                        break

    def remove_detected_element(self, category, element_name):
        """
        Remove an element from the detected elements and highlights.
        """
        # Remove from detected_elements
        if category in self.detected_elements:
            elements = self.detected_elements[category]
            self.detected_elements[category] = [
                element for element in elements if element['name'] != element_name
            ]
            if not self.detected_elements[category]:
                del self.detected_elements[category]

        # Remove from highlights
        self.highlights = [
            highlight for highlight in self.highlights if highlight['name'] != element_name
        ]

        # Remove from TreeView
        for item_id in self.category_tree.get_children():
            if self.category_tree.item(item_id, 'text') == category:
                for subitem_id in self.category_tree.get_children(item_id):
                    if self.category_tree.item(subitem_id, 'text') == element_name:
                        self.category_tree.delete(subitem_id)
                        break
                # If category has no more children, remove it
                if not self.category_tree.get_children(item_id):
                    self.category_tree.delete(item_id)
                break

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
            # Insert the category node in the TreeView
            category_node = self.category_tree.insert("", "end", text=category, open=True, tags=('category',))
        else:
            # Get the category node
            for item_id in self.category_tree.get_children():
                if self.category_tree.item(item_id, 'text') == category:
                    category_node = item_id
                    break
            else:
                # Category node not found, create it
                category_node = self.category_tree.insert("", "end", text=category, open=True, tags=('category',))

        # Check for duplicates
        if stored_element_data not in self.detected_elements[category]:
            self.detected_elements[category].append(stored_element_data)
            # Insert the element under the category node
            self.category_tree.insert(category_node, "end", text=name, tags=('element',))
            # Apply styles to the new items
            self.apply_treeview_styles()

        # Add highlight (bounding box) coordinates
        # Check for duplicates
        if not any(h['name'] == name for h in self.highlights):
            self.highlights.append({
                'coords': highlight_coords,
                'name': name,
                'selected': False  # Initially not selected
            })

    def apply_treeview_styles(self):
        """Apply styles to category and element items in the TreeView."""
        # Configure styles
        self.category_tree.tag_configure('category', font=("Helvetica", 13, "bold"))
        self.category_tree.tag_configure('element', font=("Helvetica", 12))

    def update_element_info_from_list(self, event):
        """Display information and change the highlight color when an element is selected from the TreeView."""
        selected_item = self.category_tree.focus()
        item_text = self.category_tree.item(selected_item, 'text')

        # Check if the selected item is an element or a category
        parent_item = self.category_tree.parent(selected_item)
        if parent_item:
            # It's an element
            category = self.category_tree.item(parent_item, 'text')
            element_name = item_text
        else:
            # It's a category, do nothing
            return

        # Find the element's detailed info in the detected elements data
        for element_data in self.detected_elements.get(category, []):
            if element_data['name'] == element_name:
                # Build the details string
                details_str = '\n'.join(f"{key}: {value}" for key, value in element_data['details'].items())
                # Display the element's information in Section 3
                element_info_text = f"Name: {element_data['name']}\nCategory: {category}\nDetails:\n{details_str}"

                # Update the element_info Text widget
                self.element_info.config(state='normal')  # Enable editing
                self.element_info.delete('1.0', tk.END)   # Clear previous content
                self.element_info.insert(tk.END, element_info_text)
                self.element_info.config(state='disabled')  # Disable editing

                # Change the color of the corresponding highlight
                for highlight in self.highlights:
                    highlight['selected'] = (highlight['name'] == element_name)
                break  # Element found, no need to continue inner loop

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
            for highlight in self.highlights:
                x1, y1, x2, y2 = highlight['coords']
                if x1 <= frame_x <= x2 and y1 <= frame_y <= y2:
                    # Highlight clicked, mark it as selected and update information in Section 3
                    self.select_highlight(highlight['name'])
                    break  # No need to check other highlights
        else:
            # Click was outside the image area
            pass

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

                    # Update the element_info Text widget
                    self.element_info.config(state='normal')  # Enable editing
                    self.element_info.delete('1.0', tk.END)   # Clear previous content
                    self.element_info.insert(tk.END, element_info_text)
                    self.element_info.config(state='disabled')  # Disable editing
                    break  # Element found, no need to continue inner loop

        # Programmatically select the corresponding element in the TreeView (Section 1)
        self.select_treeview_item(name)

    def select_treeview_item(self, name):
        """Programmatically select the corresponding item in the TreeView (Section 1)."""
        for category_item in self.category_tree.get_children():
            for element_item in self.category_tree.get_children(category_item):
                if self.category_tree.item(element_item, 'text') == name:
                    # Select the item and focus on it in the TreeView
                    self.category_tree.selection_set(element_item)
                    self.category_tree.focus(element_item)
                    return

    def save_elements_to_json(self, file_path):
        """Save the detected elements and their information to a JSON file."""
        with open(file_path, 'w') as f:
            json.dump(self.detected_elements, f)

    def release_resources(self):
        # Stop the camera loop
        self.running = False
        if hasattr(self, 'camera_thread'):
            self.camera_thread.join()
        # Release the camera
        if self.cap and self.cap.isOpened():
            self.cap.release()
        print("Resources released")

# ui_module.py

import tkinter as tk
from tkinter import ttk, Label, Frame
from PIL import Image, ImageTk
import json
import cv2

class UIModule:
    def __init__(self, root):
        # In-memory storage for detected elements
        self.detected_elements = {}

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

        # Initialize the camera feed and label
        self.camera_label = Label(self.middle_frame)
        self.camera_label.pack()

        # Initialize the information panel
        self.info_label = Label(self.right_frame, text="Element Information", font=("Arial", 14))
        self.info_label.pack(pady=10)
        self.element_info = Label(self.right_frame, text="", font=("Arial", 12), bg="white", width=40, height=10, anchor="nw", justify="left")
        self.element_info.pack(pady=10)

        # Bind selection event in TreeView to display element info
        self.category_tree.bind("<<TreeviewSelect>>", self.update_element_info)

        # Start camera feed
        self.show_camera_feed()

    def update_element_info(self, event):
        selected_item = self.category_tree.focus()
        item_text = self.category_tree.item(selected_item, 'text')
        self.element_info.config(text=f"Details for {item_text}: \nHere you will display info related to this element.")

    def show_camera_feed(self):
        cap = cv2.VideoCapture(0)

        def update_frame():
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                img = img.resize((600, 400))
                imgtk = ImageTk.PhotoImage(image=img)

                self.camera_label.imgtk = imgtk
                self.camera_label.configure(image=imgtk)

            self.camera_label.after(10, update_frame)

        update_frame()

    def update_detected_elements(self, category, element):
        """Add elements detected by the detection module."""
        if category not in self.detected_elements:
            self.detected_elements[category] = []
        if element not in self.detected_elements[category]:
            self.detected_elements[category].append(element)
            self.populate_treeview()

    def populate_treeview(self):
        """Update the TreeView dynamically with the current detected elements."""
        self.category_tree.delete(*self.category_tree.get_children())
        for category, elements in self.detected_elements.items():
            category_node = self.category_tree.insert("", "end", text=category, open=True)
            for element in elements:
                self.category_tree.insert(category_node, "end", text=element)

    def save_elements_to_json(self, file_path):
        """Save the detected elements to a JSON file."""
        with open(file_path, 'w') as f:
            json.dump(self.detected_elements, f)


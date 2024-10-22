# ui_module.py

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
from camera_module import CameraModule
from treeview_module import TreeViewModule
from element_info_module import ElementInfoModule
from element_manager import ElementManager
from menu_module import MenuModule  # Import the custom menu module

class UIModule:
    def __init__(self, root):
        self.root = root

        # Get the style for accessing theme colors
        self.style = ttk.Style()

        # Initialize the custom menu module
        self.menu_module = MenuModule(self.root, self)

        # Create the main frames below the menu bar
        self.left_frame = ttk.Frame(root)
        self.middle_frame = ttk.Frame(root)
        self.right_frame = ttk.Frame(root)

        # Add frames to the grid and configure weight and minsize for percentage-based layout
        self.left_frame.grid(row=1, column=0, sticky='nsew')
        self.middle_frame.grid(row=1, column=1, sticky='nsew')
        self.right_frame.grid(row=1, column=2, sticky='nsew')

        # Configure grid for window resizing
        root.grid_columnconfigure(0, weight=1, minsize=200)
        root.grid_columnconfigure(1, weight=3, minsize=400)
        root.grid_columnconfigure(2, weight=1, minsize=200)
        root.grid_rowconfigure(0, weight=0)  # Menu bar row does not expand
        root.grid_rowconfigure(1, weight=1)

        # Initialize components
        self.element_manager = ElementManager(self)
        self.treeview_module = TreeViewModule(self.left_frame, self)
        self.camera_module = CameraModule(self.middle_frame, self)
        self.element_info_module = ElementInfoModule(self.right_frame, self)

    def save_elements_to_json(self, file_path):
        """Save the detected elements and their information to a JSON file."""
        self.element_manager.save_elements_to_json(file_path)

    def release_resources(self):
        # Release resources
        self.camera_module.release_resources()
        print("Resources released")
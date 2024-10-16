# menu_module.py

import tkinter as tk
from tkinter import messagebox

class MenuModule:
    def __init__(self, root, ui_module):
        self.root = root
        self.ui_module = ui_module

        # Create the main menu
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # Add "File" menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        # Add "Edit" menu
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)

        # Add "Help" menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)

        # Populate the "File" menu
        self.file_menu.add_command(label="Open", command=self.open_file)
        self.file_menu.add_command(label="Save", command=self.save_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.exit_application)

        # Populate the "Edit" menu
        self.edit_menu.add_command(label="Undo", command=self.undo_action)
        self.edit_menu.add_command(label="Redo", command=self.redo_action)

        # Populate the "Help" menu
        self.help_menu.add_command(label="About", command=self.show_about_info)

    # Define command methods
    def open_file(self):
        # Implement open file logic
        print("Open file action")

    def save_file(self):
        # Implement save file logic
        self.ui_module.save_elements_to_json('detected_elements.json')
        print("Save file action")

    def exit_application(self):
        # Exit application logic
        self.ui_module.release_resources()
        self.root.quit()

    def undo_action(self):
        # Undo action logic
        print("Undo action")

    def redo_action(self):
        # Redo action logic
        print("Redo action")

    def show_about_info(self):
        # Show about info
        messagebox.showinfo("About", "PID Scheme Detection Application\nVersion 1.0")

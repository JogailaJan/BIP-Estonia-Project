# menu_module.py

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import messagebox

class MenuModule:
    def __init__(self, root, ui_module):
        self.root = root
        self.ui_module = ui_module

        # Get the style for accessing theme colors
        self.style = ttk.Style()

        # Create the menu bar frame
        self.menu_bar_frame = ttk.Frame(self.root, style="TFrame")
        self.menu_bar_frame.grid(row=0, column=0, columnspan=3, sticky='ew')

        # Define a custom style for the menu buttons
        self.style.configure(
            "CustomButton.TButton",
            background=self.style.colors.bg,
            foreground=self.style.colors.fg,
            borderwidth=0,
            focusthickness=0,
            highlightthickness=0
        )
        self.style.map(
            "CustomButton.TButton",
            background=[('active', self.style.colors.selectbg)],
            foreground=[('active', self.style.colors.selectfg)]
        )

        # Initialize the menu bar buttons
        self.menu_buttons = {}
        self.menu_items = ['File', 'Edit', 'Help']
        self.current_menu = None  # To track the currently open menu

        for idx, menu_name in enumerate(self.menu_items):
            btn = ttk.Button(
                self.menu_bar_frame,
                text=menu_name,
                style="CustomButton.TButton",
                command=lambda mn=menu_name: self.show_menu(mn)
            )
            # Set padx to a small value and align buttons to the left
            btn.grid(row=0, column=idx, padx=(5 if idx == 0 else 2), pady=2, sticky='w')
            self.menu_buttons[menu_name] = btn

            # Bind events for hover behavior
            btn.bind("<Enter>", lambda event, mn=menu_name: self.on_menu_button_hover(mn))

        # Configure the menu bar frame to expand horizontally
        # Set weight=0 for columns with buttons so they don't expand
        for idx in range(len(self.menu_items)):
            self.menu_bar_frame.columnconfigure(idx, weight=0)

        # Add an extra column to push buttons to the left
        self.menu_bar_frame.columnconfigure(len(self.menu_items), weight=1)

    def show_menu(self, menu_name):
        # Close any existing menu
        self.close_current_menu()

        # Create a new Menu widget
        self.current_menu = tk.Menu(
            self.root,
            tearoff=0,
            background=self.style.colors.bg,
            foreground=self.style.colors.fg,
            activebackground=self.style.colors.selectbg,
            activeforeground=self.style.colors.selectfg,
            bd=0,
            relief='flat'
        )

        if menu_name == 'File':
            self.current_menu.add_command(label="Open", command=self.open_file)
            self.current_menu.add_command(label="Save", command=self.save_file)
            self.current_menu.add_separator()
            self.current_menu.add_command(label="Exit", command=self.exit_application)
        elif menu_name == 'Edit':
            self.current_menu.add_command(label="Undo", command=self.undo_action)
            self.current_menu.add_command(label="Redo", command=self.redo_action)
        elif menu_name == 'Help':
            self.current_menu.add_command(label="About", command=self.show_about_info)

        # Get the button widget to position the menu
        btn = self.menu_buttons[menu_name]
        # Get the button's position
        x = btn.winfo_rootx()
        y = btn.winfo_rooty() + btn.winfo_height()

        # Display the menu
        self.current_menu.tk_popup(x, y)
        self.current_menu.grab_release()

        # Bind the root window to detect clicks outside the menu
        self.root.bind("<Button-1>", self.on_click_outside_menu)

    def on_menu_button_hover(self, menu_name):
        if self.current_menu:
            # Show the new menu
            self.show_menu(menu_name)

    def close_current_menu(self):
        if self.current_menu:
            self.current_menu.unpost()
            self.current_menu = None
            self.root.unbind("<Button-1>")

    def on_click_outside_menu(self, event):
        # Close the menu if clicked outside
        widget = event.widget
        if self.current_menu and not any(widget is btn for btn in self.menu_buttons.values()):
            self.close_current_menu()

    # Command methods for the menu items
    def open_file(self):
        print("Open file action")
        self.close_current_menu()

    def save_file(self):
        self.ui_module.save_elements_to_json('detected_elements.json')
        print("Save file action")
        self.close_current_menu()

    def exit_application(self):
        self.ui_module.release_resources()
        self.root.quit()

    def undo_action(self):
        print("Undo action")
        self.close_current_menu()

    def redo_action(self):
        print("Redo action")
        self.close_current_menu()

    def show_about_info(self):
        messagebox.showinfo("About", "PID Scheme Detection Application\nVersion 1.0")
        self.close_current_menu()

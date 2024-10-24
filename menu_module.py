#menu_module.py


from tkinter import simpledialog, filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
from database_module import store_image, get_all_elements, get_element_by_name  # Handles saving and loading images from the database
import threading

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

        # Initialize the menu bar buttons
        self.menu_buttons = {}
        self.menu_items = ['File']
        self.current_menu = None

        for idx, menu_name in enumerate(self.menu_items):
            btn = ttk.Button(
                self.menu_bar_frame,
                text=menu_name,
                style="CustomButton.TButton",
                command=lambda mn=menu_name: self.show_menu(mn)
            )
            btn.grid(row=0, column=idx, padx=5, pady=2, sticky='w')
            self.menu_buttons[menu_name] = btn

        # Configure the menu bar frame to expand horizontally
        for idx in range(len(self.menu_items)):
            self.menu_bar_frame.columnconfigure(idx, weight=0)
        self.menu_bar_frame.columnconfigure(len(self.menu_items), weight=1)

    def show_menu(self, menu_name):
        self.close_current_menu()
        self.current_menu = tk.Menu(self.root, tearoff=0)

        if menu_name == 'File':
            self.current_menu.add_command(label="Save Scheme to Database", command=self.save_scheme)
            self.current_menu.add_command(label="Load Scheme from Database", command=self.load_scheme)
            self.current_menu.add_separator()
            self.current_menu.add_command(label="Reset to Live Detection", command=self.reset_to_live_detection)

        btn = self.menu_buttons[menu_name]
        x = btn.winfo_rootx()
        y = btn.winfo_rooty() + btn.winfo_height()
        self.current_menu.tk_popup(x, y)
        self.current_menu.grab_release()
        self.root.bind("<Button-1>", self.on_click_outside_menu)

    def close_current_menu(self):
        if self.current_menu:
            self.current_menu.unpost()
            self.current_menu = None
            self.root.unbind("<Button-1>")

    def on_click_outside_menu(self, event):
        widget = event.widget
        if self.current_menu and not any(widget is btn for btn in self.menu_buttons.values()):
            self.close_current_menu()

    def save_scheme(self):
        scheme_name = simpledialog.askstring("Save Scheme", "Enter a name for the scheme:")
        frame = self.ui_module.camera_module.get_current_frame()
        if frame is None:
            messagebox.showwarning("Warning", "No live feed available to save.")
            return

        # Store the scheme in the database
        if scheme_name:
            store_image(frame, scheme_name)
            messagebox.showinfo("Success", f"Scheme '{scheme_name}' saved successfully!")

    def load_scheme(self):
        """Fetch schemes in a background thread and display a dialog in the main thread."""
        def fetch_schemes():
            try:
                # Fetch the list of schemes from the database
                elements = get_all_elements()
                if not elements:
                    self.root.after(0, lambda: messagebox.showinfo("No Schemes", "No saved schemes are available."))
                    return

                # Filter out schemes that have image_name
                schemes = []
                for element in elements:
                    if isinstance(element, dict) and "image_name" in element:
                        schemes.append(element["image_name"])

                if not schemes:
                    self.root.after(0, lambda: messagebox.showinfo("No Schemes", "No saved schemes are available."))
                    return

                # Schedule the dialog prompt to run in the main thread
                self.root.after(0, lambda: self.prompt_for_scheme(schemes))
                
            except Exception as e:
                print(f"Error fetching schemes: {e}")
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to fetch schemes: {str(e)}"))

        # Run the fetch_schemes function in a background thread
        threading.Thread(target=fetch_schemes, daemon=True).start()

    def prompt_for_scheme(self, schemes):
        """Prompt the user to select a scheme in the main thread."""
        schemes_list = "\n".join(f"* {scheme}" for scheme in schemes)
        scheme_name = simpledialog.askstring(
            "Load Scheme",
            f"Available schemes:\n{schemes_list}\n\nEnter scheme name:"
        )

        if not scheme_name:
            return

        scheme_name = scheme_name.strip()
        
        # Debug print statements
        print(f"User entered scheme name: '{scheme_name}'")
        print(f"Available schemes: {schemes}")
        
        if scheme_name in schemes:
            print(f"Attempting to load scheme: '{scheme_name}'")
            try:
                # First verify the scheme exists in database
                scheme_data = get_element_by_name(scheme_name)
                if scheme_data and "image_data" in scheme_data:
                    # Stop the camera feed before loading image
                    self.ui_module.camera_module.live_mode = False
                    # Load the selected scheme from the database and display it
                    success = self.ui_module.camera_module.load_image_from_database(scheme_name)
                    if not success:
                        messagebox.showerror("Error", f"Failed to load scheme '{scheme_name}'")
                else:
                    print(f"Scheme data not found in database for '{scheme_name}'")
                    messagebox.showwarning("Warning", 
                                         f"Scheme '{scheme_name}' exists but data could not be loaded.\n\nAvailable schemes are:\n{schemes_list}")
            except Exception as e:
                print(f"Error loading scheme: {e}")
                messagebox.showerror("Error", f"Failed to load scheme: {str(e)}")
        else:
            messagebox.showwarning("Warning", 
                                 f"Scheme '{scheme_name}' not found.\n\nAvailable schemes are:\n{schemes_list}")


    def reset_to_live_detection(self):
        self.ui_module.camera_module.reset_to_live_detection()
        messagebox.showinfo("Live Detection", "Camera feed restored to live detection mode.")
        self.close_current_menu()

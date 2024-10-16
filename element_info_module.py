# element_info_module.py

import ttkbootstrap as ttk
import tkinter as tk

class ElementInfoModule:
    def __init__(self, parent_frame, ui_module):
        self.ui_module = ui_module
        self.style = ttk.Style()

        # Initialize the information panel
        self.info_label = ttk.Label(
            parent_frame,
            text="Element Information",
            font=("Helvetica", 16, "bold"),
            foreground="white"
        )
        self.info_label.pack(pady=(20, 10))

        text_field_background = self.style.colors.inputbg
        text_field_foreground = self.style.colors.inputfg

        self.element_info = tk.Text(
            parent_frame,
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

    def display_element_info(self, element_info_text):
        self.element_info.config(state='normal')
        self.element_info.delete('1.0', 'end')
        self.element_info.insert('end', element_info_text)
        self.element_info.config(state='disabled')

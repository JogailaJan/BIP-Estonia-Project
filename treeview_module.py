# treeview_module.py

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class TreeViewModule:
    def __init__(self, parent_frame, ui_module):
        self.ui_module = ui_module
        self.style = ttk.Style()

        # Customize the Treeview style
        font_size_category = 13  # Adjusted for better fit
        font_size_element = 12
        max_row_height = int(max(font_size_category, font_size_element) * 1.6)

        self.style.configure("Custom.Treeview",
                             background=self.style.colors.bg,
                             foreground=self.style.colors.fg,
                             fieldbackground=self.style.colors.bg,
                             bordercolor=self.style.colors.border,
                             font=("Helvetica", font_size_element),
                             rowheight=max_row_height,
                             highlightthickness=0,
                             bd=0,
                             borderwidth=0)

        self.style.map('Custom.Treeview', background=[('selected', self.style.colors.selectbg)])

        self.style.layout("Custom.Treeview", [('Custom.Treeview.treearea', {'sticky': 'nswe'})])

        # Initialize TreeView
        self.category_tree = ttk.Treeview(
            parent_frame,
            bootstyle="info",
            style="Custom.Treeview",
            selectmode="browse",
            show="tree"
        )
        self.category_tree.heading("#0", text="Detected Elements", anchor="w")
        self.category_tree.pack(fill='both', expand=True, padx=10, pady=10)

        # Bind selection event
        self.category_tree.bind("<<TreeviewSelect>>", self.on_treeview_select)

    def on_treeview_select(self, event):
        selected_item = self.category_tree.focus()
        item_text = self.category_tree.item(selected_item, 'text')

        # Check if the selected item is an element or a category
        parent_item = self.category_tree.parent(selected_item)
        if parent_item:
            # It's an element
            category = self.category_tree.item(parent_item, 'text')
            element_name = item_text
            # Update element info and highlight
            self.ui_module.element_manager.select_element_from_treeview(category, element_name)
        else:
            # It's a category, do nothing
            return

    def apply_treeview_styles(self):
        """Apply styles to category and element items in the TreeView."""
        # Configure styles
        self.category_tree.tag_configure('category', font=("Helvetica", 13, "bold"))
        self.category_tree.tag_configure('element', font=("Helvetica", 12))

    # Methods to update the TreeView
    def add_element(self, category, element_name):
        # Add element to the TreeView
        # Get or create category node
        category_node = self.get_or_create_category_node(category)
        # Check if element already exists
        for item_id in self.category_tree.get_children(category_node):
            if self.category_tree.item(item_id, 'text') == element_name:
                return  # Element already exists
        # Insert the element under the category node
        self.category_tree.insert(category_node, "end", text=element_name, tags=('element',))
        # Apply styles
        self.apply_treeview_styles()

    def remove_element(self, category, element_name):
        # Remove element from the TreeView
        for category_id in self.category_tree.get_children():
            if self.category_tree.item(category_id, 'text') == category:
                for element_id in self.category_tree.get_children(category_id):
                    if self.category_tree.item(element_id, 'text') == element_name:
                        self.category_tree.delete(element_id)
                        break
                # If category has no more children, remove it
                if not self.category_tree.get_children(category_id):
                    self.category_tree.delete(category_id)
                break

    def get_or_create_category_node(self, category):
        # Get existing category node or create a new one
        for item_id in self.category_tree.get_children():
            if self.category_tree.item(item_id, 'text') == category:
                return item_id
        # Create new category node
        category_node = self.category_tree.insert("", "end", text=category, open=True, tags=('category',))
        return category_node

    def select_treeview_item(self, element_name):
        """Programmatically select the corresponding item in the TreeView."""
        for category_item in self.category_tree.get_children():
            for element_item in self.category_tree.get_children(category_item):
                if self.category_tree.item(element_item, 'text') == element_name:
                    # Select the item and focus on it in the TreeView
                    self.category_tree.selection_set(element_item)
                    self.category_tree.focus(element_item)
                    return

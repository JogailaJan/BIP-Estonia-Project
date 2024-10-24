# treeview_module.py

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class TreeViewModule:
    def __init__(self, parent_frame, ui_module):
        self.ui_module = ui_module
        self.style = ttk.Style()

        font_size_category = 13
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

        self.category_tree = ttk.Treeview(
            parent_frame,
            bootstyle="info",
            style="Custom.Treeview",
            selectmode="browse",
            show="tree"
        )
        self.category_tree.heading("#0", text="Detected Elements", anchor="w")
        self.category_tree.pack(fill='both', expand=True, padx=10, pady=10)

        self.category_tree.bind("<<TreeviewSelect>>", self.on_treeview_select)

    def on_treeview_select(self, event):
        selected_item = self.category_tree.focus()
        item_text = self.category_tree.item(selected_item, 'text')
        unique_id = self.category_tree.item(selected_item, 'values')[0]  # Get the unique ID stored in the TreeView

        parent_item = self.category_tree.parent(selected_item)
        if parent_item:
            category = self.category_tree.item(parent_item, 'text')
            self.ui_module.element_manager.select_element_from_treeview(category, unique_id)

    def apply_treeview_styles(self):
        self.category_tree.tag_configure('category', font=("Helvetica", 13, "bold"))
        self.category_tree.tag_configure('element', font=("Helvetica", 12))

    def select_treeview_item_by_id(self, element_id):
        """Select TreeView item by unique ID."""
        for category_item in self.category_tree.get_children():
            for element_item in self.category_tree.get_children(category_item):
                if self.category_tree.item(element_item, 'values')[0] == element_id:
                    self.category_tree.selection_set(element_item)
                    self.category_tree.focus(element_item)
                    return

    def get_or_create_category_node(self, category):
        for item_id in self.category_tree.get_children():
            if self.category_tree.item(item_id, 'text') == category:
                return item_id
        category_node = self.category_tree.insert("", "end", text=category, open=True, tags=('category',))
        return category_node

    def add_element(self, category, display_name, unique_id):
        """Add element to TreeView with a unique ID, allowing duplicates."""
        category_node = self.get_or_create_category_node(category)
        self.category_tree.insert(category_node, "end", text=display_name, values=[unique_id], tags=('element',))
        self.apply_treeview_styles()

    def remove_element(self, category, element_name, unique_id):
        """Remove an element from the TreeView based on category and unique ID."""
        for category_id in self.category_tree.get_children():
            if self.category_tree.item(category_id, 'text') == category:
                for element_id in self.category_tree.get_children(category_id):
                    if self.category_tree.item(element_id, 'values')[0] == unique_id:
                        self.category_tree.delete(element_id)
                        break
                if not self.category_tree.get_children(category_id):
                    self.category_tree.delete(category_id)
                break

# element_manager.py

import json
from categories_data import categories_info

class ElementManager:
    def __init__(self, ui_module):
        self.ui_module = ui_module
        self.detected_elements = {}
        self.highlights = []

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
        self.ui_module.treeview_module.remove_element(category, element_name)

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

        # Check for duplicates
        if stored_element_data not in self.detected_elements[category]:
            self.detected_elements[category].append(stored_element_data)
            # Add element to TreeView
            self.ui_module.treeview_module.add_element(category, name)
            # Apply styles to the new items
            self.ui_module.treeview_module.apply_treeview_styles()

        # Add highlight (bounding box) coordinates
        # Check for duplicates
        if not any(h['name'] == name for h in self.highlights):
            self.highlights.append({
                'coords': highlight_coords,
                'name': name,
                'selected': False  # Initially not selected
            })

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
                    # Display the element's information
                    element_info_text = f"Name: {element_data['name']}\nCategory: {category}\nDetails:\n{details_str}"

                    # Update the element_info Text widget
                    self.ui_module.element_info_module.display_element_info(element_info_text)
                    break  # Element found, no need to continue inner loop

        # Programmatically select the corresponding element in the TreeView
        self.ui_module.treeview_module.select_treeview_item(name)

    def select_element_from_treeview(self, category, element_name):
        """Handle selection of an element from the TreeView."""
        # Find the element's detailed info in the detected elements data
        for element_data in self.detected_elements.get(category, []):
            if element_data['name'] == element_name:
                # Build the details string
                details_str = '\n'.join(f"{key}: {value}" for key, value in element_data['details'].items())
                # Display the element's information
                element_info_text = f"Name: {element_data['name']}\nCategory: {category}\nDetails:\n{details_str}"

                # Update the element_info Text widget
                self.ui_module.element_info_module.display_element_info(element_info_text)

                # Change the color of the corresponding highlight
                for highlight in self.highlights:
                    highlight['selected'] = (highlight['name'] == element_name)
                break  # Element found, no need to continue inner loop

        # The camera module's `update_gui_frame` method will reflect the changes in highlights

    def save_elements_to_json(self, file_path):
        """Save the detected elements and their information to a JSON file."""
        with open(file_path, 'w') as f:
            json.dump(self.detected_elements, f)

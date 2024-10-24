# element_manager.py


import json
import uuid  # Import UUID for generating unique identifiers
from categories_data import categories_info

def get_iou(box1, box2):
    """Calculate Intersection over Union (IoU) between two bounding boxes."""
    x_left = max(box1[0], box2[0])
    y_top = max(box1[1], box2[1])
    x_right = min(box1[2], box2[2])
    y_bottom = min(box1[3], box2[3])

    if x_right < x_left or y_bottom < y_top:
        return 0.0

    intersection_area = (x_right - x_left) * (y_bottom - y_top)
    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union_area = box1_area + box2_area - intersection_area

    return intersection_area / union_area

class ElementManager:
    def __init__(self, ui_module):
        self.ui_module = ui_module
        self.detected_elements = {}
        self.highlights = []
        self.missing_tolerance = 10  # Number of frames to tolerate missing detection
        self.frame_timeout = {}  # Track how long each element has been missing

    def get_category(self, name):
        """Get the category of an element."""
        for cat, elements in categories_info.items():
            if name in elements:
                return cat
        return 'Unknown'

    def remove_detected_element(self, category, element_name, unique_id, highlight_coords=None):
        """Remove an element from detected elements and highlights."""
        if category in self.detected_elements:
            # Convert highlight_coords to list if it's a tuple
            if isinstance(highlight_coords, tuple):
                highlight_coords = list(highlight_coords)

            # Find elements to remove based on unique_id
            elements_to_remove = []
            for element in self.detected_elements[category]:
                if element['id'] == unique_id:
                    elements_to_remove.append(element)

            for element in elements_to_remove:
                # Remove from detected_elements
                self.detected_elements[category].remove(element)
                # Remove from TreeView
                self.ui_module.treeview_module.remove_element(category, element_name, unique_id)
                # Remove matching highlight
                self.highlights = [
                    h for h in self.highlights
                    if h['id'] != unique_id
                ]

            if not self.detected_elements[category]:
                del self.detected_elements[category]

    def update_detected_elements_list(self, detected_elements):
        """Update detected elements and remove missing ones after a tolerance period."""
        current_elements = set()
        for category in self.detected_elements:
            for element in self.detected_elements[category]:
                current_elements.add((category, element['name'], element['id'], tuple(element['highlight_coords'])))

        new_elements = set()
        for element_data in detected_elements:
            name = element_data['name']
            highlight_coords = tuple(element_data['highlight_coordinates'])
            category = self.get_category(name)
            unique_id = element_data.get('id')
            if not unique_id:
                unique_id = str(uuid.uuid4())
                element_data['id'] = unique_id  # Assign a new unique ID

            new_elements.add((category, name, unique_id, highlight_coords))

        elements_to_add = new_elements - current_elements
        elements_to_remove = current_elements - new_elements

        # Remove missing elements after tolerance
        for category, element_name, unique_id, coords in elements_to_remove:
            key = (category, element_name, unique_id, coords)
            if key not in self.frame_timeout:
                self.frame_timeout[key] = 0
            self.frame_timeout[key] += 1

            if self.frame_timeout[key] >= self.missing_tolerance:
                # Convert coords back to list for removal
                coords_list = list(coords)
                self.remove_detected_element(category, element_name, unique_id, coords_list)
                if key in self.frame_timeout:
                    del self.frame_timeout[key]

        # Reset timeout for detected elements
        for category, name, unique_id, coords in new_elements:
            key = (category, name, unique_id, coords)
            if key in self.frame_timeout:
                del self.frame_timeout[key]

        # Add new elements
        for element_data in detected_elements:
            name = element_data['name']
            highlight_coords = element_data['highlight_coordinates']
            category = self.get_category(name)
            unique_id = element_data['id']

            if (category, name, unique_id, tuple(highlight_coords)) in elements_to_add:
                self.update_detected_elements(element_data)

    def update_detected_elements(self, element_data):
        """Add new detected elements and update TreeView, ensuring synchronization with highlights."""
        name = element_data['name']
        details = element_data['details']
        highlight_coords = element_data['highlight_coordinates']
        category = self.get_category(name)
        unique_id = element_data['id']

        stored_element_data = {
            'id': unique_id,
            'name': name,
            'details': details,
            'highlight_coords': highlight_coords
        }

        # Check for overlap with existing highlights
        if any(get_iou(h['coords'], highlight_coords) > 0.5 and h['id'] != unique_id for h in self.highlights):
            return  # Skip this element if significant overlap exists with another element

        # Add to detected_elements dictionary
        if category not in self.detected_elements:
            self.detected_elements[category] = []
        self.detected_elements[category].append(stored_element_data)

        # Add to TreeView
        self.ui_module.treeview_module.add_element(category, name, unique_id)
        self.ui_module.treeview_module.apply_treeview_styles()

        # Add to highlights
        self.highlights.append({
            'coords': highlight_coords,
            'name': name,
            'id': unique_id,
            'selected': False
        })

    def select_highlight(self, element_id):
        """Select a highlight by unique element ID."""
        for highlight in self.highlights:
            highlight['selected'] = (highlight['id'] == element_id)

        # Update the right panel with element information
        for category, elements in self.detected_elements.items():
            for element_data in elements:
                if element_data['id'] == element_id:
                    details_str = '\n'.join(f"{key}: {value}" for key, value in element_data['details'].items())
                    element_info_text = f"Name: {element_data['name']}\nCategory: {category}\nDetails:\n{details_str}"
                    self.ui_module.element_info_module.display_element_info(element_info_text)
                    break

        self.ui_module.treeview_module.select_treeview_item_by_id(element_id)

    def select_element_from_treeview(self, category, element_id):
        """Select an element from the TreeView and update highlights."""
        for element_data in self.detected_elements.get(category, []):
            if element_data['id'] == element_id:
                details_str = '\n'.join(f"{key}: {value}" for key, value in element_data['details'].items())
                element_info_text = f"Name: {element_data['name']}\nCategory: {category}\nDetails:\n{details_str}"
                self.ui_module.element_info_module.display_element_info(element_info_text)

                for highlight in self.highlights:
                    highlight['selected'] = (highlight['id'] == element_id)
                break

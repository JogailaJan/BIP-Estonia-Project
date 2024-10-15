# detection_module.py

class DetectionModule:
    def __init__(self, ui_module):
        """Initialize with a reference to the UI module."""
        self.ui_module = ui_module

    def detect_elements(self):
        """Simulate the element detection logic with bounding boxes."""
        # Simulated element detection with bounding box coordinates
        element_data_1 = {
            'name': 'Tank 1',
            'type': 'Atmospheric Tank',
            'details': 'Capacity: 500L, Material: Stainless Steel'
        }
        highlight_1 = (50, 50, 150, 150)  # Simulated bounding box for Tank 1

        element_data_2 = {
            'name': 'Tank 2',
            'type': 'Pressurized Tank',
            'details': 'Capacity: 1000L, Material: Carbon Steel'
        }
        highlight_2 = (200, 100, 300, 200)  # Simulated bounding box for Tank 2

        element_data_3 = {
            'name': 'Pump 1',
            'type': 'Centrifugal Pump',
            'details': 'Flow Rate: 150L/min, Power: 5HP'
        }
        highlight_3 = (350, 150, 450, 250)  # Simulated bounding box for Pump 1

        # Add detected elements to the UI with their information and bounding boxes
        self.ui_module.update_detected_elements('Tanks', element_data_1, highlight_coords=highlight_1)
        self.ui_module.update_detected_elements('Tanks', element_data_2, highlight_coords=highlight_2)
        self.ui_module.update_detected_elements('Pumps', element_data_3, highlight_coords=highlight_3)

    def run_detection(self):
        """Continuously run element detection. Call this after detection logic is ready."""
        self.detect_elements()  # Replace with real detection
        # Add logic to call this repeatedly during live detection if needed

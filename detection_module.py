# detection_module.py

class DetectionModule:
    def __init__(self, ui_module):
        """Initialize with a reference to the UI module."""
        self.ui_module = ui_module

    def detect_elements(self):
        """Simulate the element detection logic with bounding boxes and details."""
        # Simulated element detection with details and bounding box coordinates
        element_data_1 = {
            'name': 'Atmospheric Tank',
            'details': {
                'Capacity': '500L',
                'Material': 'Stainless Steel'
            },
            'highlight_coordinates': (50, 50, 150, 150)
        }

        element_data_2 = {
            'name': 'Pressurized Tank',
            'details': {
                'Capacity': '1000L',
                'Material': 'Carbon Steel'
            },
            'highlight_coordinates': (200, 100, 300, 200)
        }

        element_data_3 = {
            'name': 'Centrifugal Pump',
            'details': {
                'Flow Rate': '150L/min',
                'Power': '5HP'
            },
            'highlight_coordinates': (350, 150, 450, 250)
        }

        # Add detected elements to the UI
        self.ui_module.update_detected_elements(element_data_1)
        self.ui_module.update_detected_elements(element_data_2)
        self.ui_module.update_detected_elements(element_data_3)

    def run_detection(self):
        """Continuously run element detection. Call this after detection logic is ready."""
        self.detect_elements()  # Replace with real detection
        # Add logic to call this repeatedly during live detection if needed

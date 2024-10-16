# detection_module.py

import threading
import time

class DetectionModule:
    def __init__(self, ui_module):
        """Initialize with a reference to the UI module."""
        self.ui_module = ui_module
        self.running = True  # Flag to control the detection thread

    def detect_elements(self):
        """Simulate the element detection logic."""
        # Simulated stable detection with details and bounding box coordinates
        detected_elements = [
            {
                'name': 'Atmospheric Tank',
                'details': {
                    'Capacity': '500L',
                    'Material': 'Stainless Steel'
                },
                'highlight_coordinates': (50, 50, 150, 150)
            },
            {
                'name': 'Pressurized Tank',
                'details': {
                    'Capacity': '1000L',
                    'Material': 'Carbon Steel'
                },
                'highlight_coordinates': (200, 100, 300, 200)
            },
            {
                'name': 'Centrifugal Pump',
                'details': {
                    'Flow Rate': '150L/min',
                    'Power': '5HP'
                },
                'highlight_coordinates': (350, 150, 450, 250)
            }
        ]

        # Schedule the UI update on the main thread
        self.ui_module.root.after(
            0,
            self.ui_module.element_manager.update_detected_elements_list,
            detected_elements
        )

    def run_detection(self):
        """Continuously run element detection in a separate thread."""
        self.detection_thread = threading.Thread(target=self.detection_loop)
        self.detection_thread.daemon = True  # Daemonize thread
        self.detection_thread.start()

    def detection_loop(self):
        while self.running:
            # Simulate detection delay
            time.sleep(1)  # Adjust as needed for real detection time

            # Perform detection
            self.detect_elements()

    def stop_detection(self):
        self.running = False
        if hasattr(self, 'detection_thread'):
            self.detection_thread.join()

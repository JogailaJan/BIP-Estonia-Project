# detection_module.py

import threading
import time
import cv2
from ultralytics import YOLO

class DetectionModule:
    def __init__(self, ui_module):
        """Initialize with a reference to the UI module."""
        self.ui_module = ui_module
        self.running = True  # Flag to control the detection thread
        
        # Load your trained YOLO model (use the path to your `best.pt` model)
        self.model = YOLO('runs/detect/train19/weights/yolov8n.pt')

    def detect_elements(self, frame):
        """Use YOLO to detect elements in the frame."""
        # If necessary, convert frame back to BGR for YOLO (OpenCV uses BGR, but detection could require RGB)
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        # Perform YOLO inference
        results = self.model.predict(frame_bgr)
        
        detected_elements = []
        
        # Extract results
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])  # Bounding box coordinates
                label = self.model.names[int(box.cls[0])]  # Class label
                confidence = box.conf[0]  # Confidence score
                
                # Example: Store detected element details
                detected_elements.append({
                    'name': label,
                    'details': {
                        'Confidence': f"{confidence:.2f}"
                    },
                    'highlight_coordinates': (x1, y1, x2, y2)
                })
        
        # Schedule the UI update on the main thread
        self.ui_module.root.after(
            0,
            self.ui_module.element_manager.update_detected_elements_list,
            detected_elements
        )

    def run_detection(self):
        """Start the detection thread."""
        print("Starting detection thread...")  # Debugging print
        self.detection_thread = threading.Thread(target=self.detection_loop)
        self.detection_thread.daemon = True  # Daemonize thread
        self.detection_thread.start()


    def detection_loop(self):
        """Continuously run element detection in a separate thread."""
        while self.running:
            if self.ui_module.camera_module.current_frame is not None:
                print("Running detection...")  # Debugging print
                # Perform detection on the current frame from the camera
                frame = self.ui_module.camera_module.current_frame.copy()  # Ensure you're working on a copy
                self.detect_elements(frame)
            else:
                print("No frame available yet.")  # Debugging print

            # Adjust the sleep time as needed for real-time performance
            time.sleep(0.1)  # e.g., 10 FPS


    def stop_detection(self):
        self.running = False
        if hasattr(self, 'detection_thread'):
            self.detection_thread.join()
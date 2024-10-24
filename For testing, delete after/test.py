import cv2
import random
from ultralytics import YOLO

# Load YOLOv8 model
model = YOLO('runs/detect/yolo8n_v8_50e/weights/best.pt')  # You can replace 'yolov8n.pt' with a specific model file if needed
# Initialize the webcam
cap = cv2.VideoCapture(0)  # Use 0 for the default camera, or provide another index for an external camera

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

cv2.namedWindow("YOLOv8 Detection", cv2.WINDOW_NORMAL)  # Create a resizable window

# Get the original dimensions of the camera feed
original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
aspect_ratio = original_width / original_height

# Generate random colors for class IDs from 0 to 30
class_colors = {i: (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for i in range(31)}

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to grab frame.")
        break

    # Use the model to predict on the frame
    results = model(frame)

    # Draw the bounding boxes on the frame
    for result in results:
        boxes = result.boxes.xyxy  # Get the bounding box coordinates
        confs = result.boxes.conf  # Get the confidence scores
        cls = result.boxes.cls     # Get the class IDs

        for box, conf, cls_id in zip(boxes, confs, cls):
            # Convert bounding box to integers
            x1, y1, x2, y2 = map(int, box)

            # Get the color for the class, use random color generation
            color = class_colors.get(int(cls_id), (255, 255, 255))  # Default to white if no color found

            # Draw the bounding box and label with the corresponding color
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            label = f"Class: {int(cls_id)} Conf: {conf:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Resize the frame while keeping the aspect ratio
    window_width = cv2.getWindowImageRect("YOLOv8 Detection")[2]
    window_height = cv2.getWindowImageRect("YOLOv8 Detection")[3]

    # Calculate the scaling factor and new dimensions while maintaining aspect ratio
    scale_factor = min(window_width / original_width, window_height / original_height)
    new_width = int(original_width * scale_factor)
    new_height = int(original_height * scale_factor)

    # Resize the frame to fit within the window while maintaining aspect ratio
    resized_frame = cv2.resize(frame, (new_width, new_height))

    # Create a black background (padding) for letterboxing if needed
    final_frame = cv2.copyMakeBorder(
        resized_frame,
        top=(window_height - new_height) // 2,
        bottom=(window_height - new_height) // 2,
        left=(window_width - new_width) // 2,
        right=(window_width - new_width) // 2,
        borderType=cv2.BORDER_CONSTANT,
        value=[0, 0, 0]  # Black padding
    )

    # Display the frame
    cv2.imshow("YOLOv8 Detection", final_frame)

    # Toggle fullscreen mode by pressing 'f'
    key = cv2.waitKey(1) & 0xFF
    if key == ord('f'):
        cv2.setWindowProperty("YOLOv8 Detection", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    if key == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()

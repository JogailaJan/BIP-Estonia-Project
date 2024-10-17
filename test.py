import cv2
from ultralytics import YOLO

# Load YOLOv8 model
model = YOLO('runs/detect/yolo8n_v8_50e/weights/best.pt')  # You can replace 'yolov8n.pt' with a specific model file if needed
# Initialize the webcam
cap = cv2.VideoCapture(0)  # Use 0 for the default camera, or provide another index for an external camera

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

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

            # Draw the bounding box and label
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"Class: {int(cls_id)} Conf: {conf:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Display the frame
    cv2.imshow("YOLOv8 Detection", frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()

import os
import inference
import cv2
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Set your API key using environment variables (make sure .env is loaded or key is set)
api_key = os.getenv('ROBOFLOW_API_KEY')

# Check if API key is properly loaded
if not api_key:
    print("Error: API key is missing or not set.")
    exit()

# Load your model (replace "scheme-elements/2" with your model ID)
model = inference.get_model("scheme-elements/2", api_key=api_key)

# Open a connection to the webcam
cap = cv2.VideoCapture(0)  # '0' refers to the default camera, change if you have multiple cameras

# Check if the webcam opened correctly
if not cap.isOpened():
    print("Error: Could not open video stream.")
    exit()

# Loop to continuously capture frames from the webcam
while True:
    # Capture frame-by-frame from the camera
    ret, frame = cap.read()

    if not ret:
        print("Error: Could not read frame.")
        break

    # Save the frame to a temporary image file
    cv2.imwrite('temp_frame.jpg', frame)

    # Perform inference on the current frame
    results = model.infer(image='temp_frame.jpg')

    # Print the results to debug
    print("Results:", results)

    # Check if results is a list
    if isinstance(results, list):
        for result in results:
            # Check if each result has 'predictions'
            if 'predictions' in result:
                for prediction in result['predictions']:
                    label = prediction["class"]
                    confidence = prediction["confidence"]
                    x = prediction["x"]
                    y = prediction["y"]
                    width = prediction["width"]
                    height = prediction["height"]

                    # Calculate the top-left and bottom-right coordinates of the bounding box
                    x1 = int(x - width / 2)
                    y1 = int(y - height / 2)
                    x2 = int(x + width / 2)
                    y2 = int(y + height / 2)

                    # Draw the bounding box on the frame
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                    # Put the label and confidence on the frame
                    text = f"{label} ({confidence:.2f})"
                    cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # If results is a dictionary with 'predictions'
    elif isinstance(results, dict) and 'predictions' in results:
        for prediction in results['predictions']:
            label = prediction["class"]
            confidence = prediction["confidence"]
            x = prediction["x"]
            y = prediction["y"]
            width = prediction["width"]
            height = prediction["height"]

            # Calculate the top-left and bottom-right coordinates of the bounding box
            x1 = int(x - width / 2)
            y1 = int(y - height / 2)
            x2 = int(x + width / 2)
            y2 = int(y + width / 2)

            # Draw the bounding box on the frame
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Put the label and confidence on the frame
            text = f"{label} ({confidence:.2f})"
            cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)




    # Display the frame with bounding boxes
    cv2.imshow("Live Camera Feed", frame)

    # Exit the loop when the user presses 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close OpenCV windows
cap.release()
cv2.destroyAllWindows()

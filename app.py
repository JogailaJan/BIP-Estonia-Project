# app.py

import tkinter as tk
from ui_module import UIModule
from detection_module import DetectionModule

# Initialize the main Tkinter window
root = tk.Tk()
root.title("PID Scheme Detection")
root.geometry("1200x800")

# Initialize the UI module
ui = UIModule(root)

# Initialize the detection module and pass a reference to the UI module
detection = DetectionModule(ui)

# Run the detection logic (this will call the detection module which interacts with the UI)
detection.run_detection()

# Start the Tkinter event loop
root.mainloop()

# After the session ends, save the detected elements to a file
ui.save_elements_to_json('detected_elements.json')

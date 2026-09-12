import sys
import os
import json
import cv2
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QFileDialog, QVBoxLayout, QHBoxLayout, QMessageBox
)
from PyQt5.QtGui import QPixmap, QImage
import mediapipe as mp

# ======================================
# Directory for saving JSON files
# ======================================
# Set the target folder path where the generated JSON landmarks will be saved.
# Create the directory if it does not already exist.
SAVE_FOLDER = "landmarks"
os.makedirs(SAVE_FOLDER, exist_ok=True)

# ======================================
# MediaPipe Configuration
# ======================================
# Initialize the MediaPipe Pose solution and drawing utilities
# These are used to extract keypoint landmarks from images.
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# ======================================
# Main GUI Class
# ======================================
class YogaLandmarkBatchApp(QWidget):
    """
    A PyQt5 GUI application to batch process images of yoga poses.
    It extracts skeletal landmarks using MediaPipe and saves them as JSON files.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Yoga Landmark Batch Capture")
        self.setGeometry(100, 100, 800, 600)
        
        self.folder_path = None
        
        # Initialize UI components
        self.label_info = QLabel("Please select a folder containing image files.")
        self.label_info.setWordWrap(True)
        
        self.process_button = QPushButton("Select Folder and Process Images")
        self.process_button.clicked.connect(self.select_and_process_folder)
        
        # Set up the main vertical layout
        layout = QVBoxLayout()
        layout.addWidget(self.label_info)
        layout.addWidget(self.process_button)
        self.setLayout(layout)
    
    # ======================================
    # Image Batch Processing
    # ======================================
    def select_and_process_folder(self):
        """
        Opens a directory selection dialog, loads all supported images from the chosen directory,
        processes each image to extract pose landmarks, and saves the results as JSON.
        """
        # Prompt the user to select the directory containing input images
        folder = QFileDialog.getExistingDirectory(
            self, "Select Image Folder"
        )
        if not folder:
            return
        
        self.folder_path = folder
        self.label_info.setText(f"Processing images in folder: {folder}")
        
        # Filter for files ending in common image extensions
        img_files = [f for f in os.listdir(folder) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        if not img_files:
            QMessageBox.warning(self, "Error", "No images found in the selected directory.")
            return
        
        # Process the found images using MediaPipe Pose (static image mode)
        with mp_pose.Pose(static_image_mode=True) as pose:
            for img_file in img_files:
                img_path = os.path.join(folder, img_file)
                
                # Load the image using OpenCV
                img = cv2.imread(img_path)
                if img is None:
                    print(f"[WARN] Failed to load image: {img_file}")
                    continue
                
                # Convert the image from BGR (OpenCV default) to RGB (MediaPipe requirement)
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                
                # Run the pose processing on the RGB image
                results = pose.process(img_rgb)
                
                landmarks = {}
                if results.pose_landmarks:
                    # MediaPipe pose consists of 33 keypoints. We assign standardized names to each.
                    landmark_names = [
                        "nose",
                        "left_eye_inner", "left_eye", "left_eye_outer",
                        "right_eye_inner", "right_eye", "right_eye_outer",
                        "left_ear", "right_ear",
                        "mouth_left", "mouth_right",
                        "left_shoulder", "right_shoulder",
                        "left_elbow", "right_elbow",
                        "left_wrist", "right_wrist",
                        "left_pinky", "right_pinky",
                        "left_index", "right_index",
                        "left_thumb", "right_thumb",
                        "left_hip", "right_hip",
                        "left_knee", "right_knee",
                        "left_ankle", "right_ankle",
                        "left_heel", "right_heel",
                        "left_foot_index", "right_foot_index"
                    ]
                    
                    # Extract the x and y coordinates for each detected landmark
                    for idx, lm in enumerate(results.pose_landmarks.landmark):
                        landmarks[landmark_names[idx]] = [lm.x, lm.y]
                    
                    # Construct the output filename using the original image base name
                    name, _ = os.path.splitext(img_file)
                    save_path = os.path.join(SAVE_FOLDER, f"{name}.json")
                    
                    # Save the landmarks dictionary as a JSON file
                    with open(save_path, "w") as f:
                        json.dump(landmarks, f, indent=4)
                    
                    print(f"[INFO] Successfully saved: {save_path}")
                else:
                    # Log a warning if no person/pose was detected in the image
                    print(f"[WARN] No landmarks detected in: {img_file}")
        
        # Display completion message to the user
        QMessageBox.information(self, "Processing Complete", f"Finished processing {len(img_files)} images!")

# ======================================
# Application Entry Point
# ======================================
if __name__ == "__main__":
    # Create the Qt Application
    app = QApplication(sys.argv)
    
    # Instantiate and show the main window
    window = YogaLandmarkBatchApp()
    window.show()
    
    # Execute the application event loop
    sys.exit(app.exec_())
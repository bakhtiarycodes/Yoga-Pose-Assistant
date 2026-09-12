import cv2
import mediapipe as mp


class PoseDetector:

    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose = None

        try:
            self.pose = self.mp_pose.Pose(
                static_image_mode=False,
                model_complexity=1,
                smooth_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
            )
        except Exception as e:
            print(f"[ERROR] Failed to initialize MediaPipe Pose: {e}")

    def process(self, frame):
        if self.pose is None or frame is None:
            return None

        try:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return self.pose.process(rgb)
        except Exception as e:
            print(f"[ERROR] Pose detection failed: {e}")
            return None
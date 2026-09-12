import cv2
from core.pose_utils import (
    POSE_CONNECTIONS,
    compare_pose_landmarks,
    extract_user_landmarks,
)

class PoseRenderer:

    def __init__(self):
        self.current_pose = None  # ژست مرجع
        self.paused = False

    def set_pose(self, pose_data):
        """تنظیم ژست مرجع از JSON"""
        self.current_pose = pose_data
        # Debug info about incoming pose data
        try:
            if pose_data is None:
                print("[DEBUG] PoseRenderer.set_pose: None")
            elif isinstance(pose_data, dict):
                if "landmarks" in pose_data and isinstance(pose_data["landmarks"], dict):
                    count = len(pose_data["landmarks"])
                else:
                    count = len(pose_data)
                print(f"[DEBUG] PoseRenderer.set_pose: received pose dict with {count} entries")
            else:
                print("[DEBUG] PoseRenderer.set_pose: received non-dict pose_data")
        except Exception as e:
            print(f"[DEBUG] PoseRenderer.set_pose: error inspecting pose_data: {e}")

    def draw_reference_pose(self, frame):
        """ترسیم ژست مرجع روی تصویر"""
        if self.paused or frame is None:
            return frame
        if self.current_pose is None:
            return frame

        try:
            height, width, _ = frame.shape

            if isinstance(self.current_pose, dict) and "landmarks" in self.current_pose:
                landmarks_source = self.current_pose["landmarks"]
            else:
                landmarks_source = self.current_pose

            if not isinstance(landmarks_source, dict):
                return frame

            landmarks = {}
            for name, point in landmarks_source.items():
                if not isinstance(point, (list, tuple)) or len(point) < 2:
                    continue
                try:
                    x_norm = float(point[0])
                    y_norm = float(point[1])
                except (TypeError, ValueError):
                    continue
                x = int(x_norm * width)
                y = int(y_norm * height)
                landmarks[name] = (x, y)

            if not landmarks:
                print("[DEBUG] PoseRenderer.draw_reference_pose: no valid landmarks found in pose data")
                return frame

            connections = [
            ("nose", "left_eye_inner"),
            ("left_eye_inner", "left_eye"),
            ("left_eye", "left_eye_outer"),
            ("nose", "right_eye_inner"),
            ("right_eye_inner", "right_eye"),
            ("right_eye", "right_eye_outer"),
            ("nose", "left_shoulder"),
            ("nose", "right_shoulder"),
            ("left_shoulder", "right_shoulder"),
            ("left_shoulder", "left_elbow"),
            ("left_elbow", "left_wrist"),
            ("left_wrist", "left_thumb"),
            ("left_wrist", "left_index"),
            ("left_wrist", "left_pinky"),
            ("right_shoulder", "right_elbow"),
            ("right_elbow", "right_wrist"),
            ("right_wrist", "right_thumb"),
            ("right_wrist", "right_index"),
            ("right_wrist", "right_pinky"),
            ("left_shoulder", "left_hip"),
            ("right_shoulder", "right_hip"),
            ("left_hip", "right_hip"),
            ("left_hip", "left_knee"),
            ("left_knee", "left_ankle"),
            ("left_ankle", "left_heel"),
            ("left_heel", "left_foot_index"),
            ("right_hip", "right_knee"),
            ("right_knee", "right_ankle"),
            ("right_ankle", "right_heel"),
            ("right_heel", "right_foot_index")
        ]

            gray = (170, 170, 170)

            for start, end in connections:
                if start in landmarks and end in landmarks:
                    cv2.line(frame, landmarks[start], landmarks[end], gray, 2)

            for point in landmarks.values():
                cv2.circle(frame, point, 5, gray, -1)
        except Exception as e:
            print(f"[ERROR] draw_reference_pose failed: {e}")

        return frame

    def draw_user_pose(self, frame, results, mp_pose):
        """Draw user landmarks colored by distance to the reference pose."""
        if self.paused or frame is None or results is None:
            return frame, 0.0
        if results.pose_landmarks is None:
            return frame, 0.0

        try:
            height, width, _ = frame.shape
            user_landmarks = extract_user_landmarks(results, mp_pose)
            landmark_colors, accuracy = compare_pose_landmarks(
                self.current_pose,
                user_landmarks,
            )

            default_color = (200, 200, 200)

            for start, end in POSE_CONNECTIONS:
                if start not in user_landmarks or end not in user_landmarks:
                    continue

                start_color = landmark_colors.get(start, {}).get("color", default_color)
                end_color = landmark_colors.get(end, {}).get("color", default_color)
                line_color = start_color if start_color == end_color else (
                    0,
                    int((start_color[1] + end_color[1]) / 2),
                    int((start_color[2] + end_color[2]) / 2),
                )

                start_point = (
                    int(user_landmarks[start][0] * width),
                    int(user_landmarks[start][1] * height),
                )
                end_point = (
                    int(user_landmarks[end][0] * width),
                    int(user_landmarks[end][1] * height),
                )
                cv2.line(frame, start_point, end_point, line_color, 2)

            for name, point in user_landmarks.items():
                pixel = (int(point[0] * width), int(point[1] * height))
                color = landmark_colors.get(name, {}).get("color", default_color)
                cv2.circle(frame, pixel, 6, color, -1)

            return frame, accuracy
        except Exception as e:
            print(f"[ERROR] draw_user_pose failed: {e}")
            return frame, 0.0
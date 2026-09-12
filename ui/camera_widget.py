import cv2
import time
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from core.pose_renderer import PoseRenderer
from core.pose_detector import PoseDetector


class CameraWidget(QWidget):
    # Signal to update status panel
    stats_updated = pyqtSignal(float, float, float)  # fps, confidence, accuracy

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.pose_renderer = PoseRenderer()
        self.pose_detector = PoseDetector()

        self.label = QLabel("Camera View")
        self.label.setStyleSheet(
            """
            QLabel {
                background-color: black;
                color: white;
                border: 2px solid #2C2C2C;
                border-radius: 15px;
            }
            """
        )
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )
        self.label.setScaledContents(True)
        layout.addWidget(self.label)

        # OpenCV Video Capture
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        # FPS tracking
        self.frame_count = 0
        self.fps_time = time.time()
        self.current_fps = 0
        self.current_confidence = 0
        self.current_accuracy = 0

        self.is_captured = False
        self.captured_pixmap = None
        self.captured_image = None

    def _reset_capture_state(self):
        self.is_captured = False
        self.captured_pixmap = None
        self.captured_image = None

    def start_camera(self):
        try:
            self._reset_capture_state()

            if self.cap is None:
                self.cap = cv2.VideoCapture(0)

            if self.cap is None or not self.cap.isOpened():
                if self.cap is not None:
                    self.cap.release()
                self.cap = None
                print("[ERROR] Unable to open webcam")
                return False

            self.timer.start(30)
            return True
        except Exception as e:
            print(f"[ERROR] start_camera failed: {e}")
            if self.cap is not None:
                try:
                    self.cap.release()
                except Exception:
                    pass
            self.cap = None
            return False

    def stop_camera(self):
        try:
            self.timer.stop()
            if self.cap:
                self.cap.release()
        except Exception as e:
            print(f"[ERROR] stop_camera failed: {e}")
        finally:
            self.cap = None
            self.is_captured = False
            self.captured_pixmap = None
            self.label.clear()
            self.label.setText("Camera View")

    def capture_frame(self):
        if self.is_captured or self.cap is None or not self.timer.isActive():
            return False

        try:
            displayed = self.label.grab()
            if displayed.isNull():
                return False

            self.captured_pixmap = displayed.copy()
            self.captured_image = self.captured_pixmap.toImage().copy()
            self.is_captured = True

            self.timer.stop()
            if self.cap:
                self.cap.release()
                self.cap = None

            self.label.setPixmap(self.captured_pixmap)
            return True
        except Exception as e:
            print(f"[ERROR] capture_frame failed: {e}")
            return False

    def has_captured_image(self):
        return (
            self.captured_image is not None
            and not self.captured_image.isNull()
        )

    def get_captured_image(self):
        return self.captured_image

    def update_frame(self):
        if self.is_captured or self.cap is None:
            return

        try:
            success, frame = self.cap.read()
            if not success or frame is None:
                return

            frame = cv2.flip(frame, 1)
            results = self.pose_detector.process(frame)

            if results is not None and results.pose_landmarks:
                confidences = [lm.visibility for lm in results.pose_landmarks.landmark]
                self.current_confidence = (sum(confidences) / len(confidences)) * 100
            else:
                self.current_confidence = 0

            frame = self.pose_renderer.draw_reference_pose(frame)
            frame, self.current_accuracy = self.pose_renderer.draw_user_pose(
                frame,
                results,
                self.pose_detector.mp_pose,
            )

            self.frame_count += 1
            current_time = time.time()
            elapsed = current_time - self.fps_time
            if elapsed >= 1.0:
                self.current_fps = self.frame_count / elapsed
                self.frame_count = 0
                self.fps_time = current_time

            self.stats_updated.emit(
                self.current_fps,
                self.current_confidence,
                self.current_accuracy,
            )

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            image = QImage(
                frame.data,
                w,
                h,
                bytes_per_line,
                QImage.Format_RGB888,
            ).copy()

            self.label.setPixmap(QPixmap.fromImage(image))
        except Exception as e:
            print(f"[ERROR] update_frame failed: {e}")

    def get_fps(self):
        """Get current FPS"""
        return self.current_fps

    def get_confidence(self):
        """Get current confidence score (0-100)"""
        return self.current_confidence

    def get_accuracy(self):
        """Get current accuracy (0-100)"""
        return self.current_accuracy
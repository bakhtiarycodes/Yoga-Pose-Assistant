from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QSizePolicy, QComboBox, QSpinBox, QPushButton, QHBoxLayout
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor
from PyQt5.QtCore import Qt, pyqtSignal, QRect


class StatusPanel(QWidget):
    start_program_clicked = pyqtSignal()
    stop_program_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Title
        title = QLabel("📊 Status")
        title.setFont(QFont("Arial", 16, weight=QFont.Bold))
        layout.addWidget(title)

        # Status Card Frame
        status_frame = QFrame()
        status_frame.setStyleSheet(
            """
            QFrame {
                background-color: #1E1E1E;
                border: 2px solid #2C2C2C;
                border-radius: 10px;
                padding: 15px;
            }
            """
        )
        status_layout = QVBoxLayout()
        status_frame.setLayout(status_layout)

        # Current Pose (allow two lines)
        self.pose_label = QLabel("Current Pose: ---")
        self.pose_label.setFont(QFont("Arial", 14, weight=QFont.Bold))
        self.pose_label.setStyleSheet("color: #E8F5E9;")
        self.pose_label.setWordWrap(True)
        self.pose_label.setFixedHeight(130)
        status_layout.addWidget(self.pose_label)

        # Reference image preview (match label widths)
        self.image_preview = QLabel()
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.image_preview.setFixedHeight(550)
        self.image_preview.setStyleSheet("background-color: #0f0f0f; border-radius:8px;")
        status_layout.addWidget(self.image_preview)

        # FPS Counter
        self.fps_label = QLabel("FPS: 0")
        self.fps_label.setFont(QFont("Arial", 12))
        self.fps_label.setStyleSheet("color: #87CEEB;")
        status_layout.addWidget(self.fps_label)

        # Confidence Score
        self.confidence_label = QLabel("MediapipeConfidence: 0%")
        self.confidence_label.setFont(QFont("Arial", 12))
        self.confidence_label.setStyleSheet("color: #FFB6C1;")
        status_layout.addWidget(self.confidence_label)

        # Pose Accuracy
        self.accuracy_label = QLabel("Pose Matching Accuracy: 0%")
        self.accuracy_label.setFont(QFont("Arial", 12))
        self.accuracy_label.setStyleSheet("color: #FFD700;")
        status_layout.addWidget(self.accuracy_label)

        # Program Selection
        program_label = QLabel("Program Level")
        program_label.setFont(QFont("Arial", 14, weight=QFont.Bold))
        status_layout.addWidget(program_label)

        self.level_selector = QComboBox()
        self.level_selector.addItems(["Beginner", "Intermediate", "Advanced"])
        self.level_selector.setCurrentIndex(0)
        status_layout.addWidget(self.level_selector)

        hold_layout = QHBoxLayout()
        hold_label = QLabel("Hold Time (sec)")
        hold_label.setFont(QFont("Arial", 12))
        hold_layout.addWidget(hold_label)
        self.hold_time_spin = QSpinBox()
        self.hold_time_spin.setRange(10, 180)
        self.hold_time_spin.setValue(20)
        hold_layout.addWidget(self.hold_time_spin)
        status_layout.addLayout(hold_layout)

        rest_layout = QHBoxLayout()
        rest_label = QLabel("Rest Time (sec)")
        rest_label.setFont(QFont("Arial", 12))
        rest_layout.addWidget(rest_label)
        self.rest_time_spin = QSpinBox()
        self.rest_time_spin.setRange(5, 120)
        self.rest_time_spin.setValue(15)
        rest_layout.addWidget(self.rest_time_spin)
        status_layout.addLayout(rest_layout)

        rep_layout = QHBoxLayout()
        rep_label = QLabel("Repetitions")
        rep_label.setFont(QFont("Arial", 12))
        rep_layout.addWidget(rep_label)
        self.repetitions_spin = QSpinBox()
        self.repetitions_spin.setRange(1, 10)
        self.repetitions_spin.setValue(1)
        rep_layout.addWidget(self.repetitions_spin)
        status_layout.addLayout(rep_layout)

        button_layout = QHBoxLayout()
        self.start_program_button = QPushButton("Start Program")
        self.stop_program_button = QPushButton("Stop Program")
        self.stop_program_button.setEnabled(False)
        button_layout.addWidget(self.start_program_button)
        button_layout.addWidget(self.stop_program_button)
        status_layout.addLayout(button_layout)

        self.program_status_label = QLabel("Program status: Idle")
        self.program_status_label.setFont(QFont("Arial", 12))
        self.program_status_label.setStyleSheet("color: #FFFFFF;")
        self.program_status_label.setWordWrap(True)
        self.program_status_label.setFixedHeight(130)
        status_layout.addWidget(self.program_status_label)
        self.program_timer_label = QLabel("00:00")
        self.program_timer_label.setObjectName("programTimerLabel")
        self.program_timer_label.setProperty("mode", "hold")
        self.program_timer_label.setFont(QFont("Arial", 250, weight=QFont.Bold))
        self.program_timer_label.setAlignment(Qt.AlignCenter)
        self.program_timer_label.setFixedHeight(250)
        status_layout.addWidget(self.program_timer_label)
        layout.addWidget(status_frame)
        layout.addStretch()

        self.level_selector.currentIndexChanged.connect(self._on_level_changed)
        self.start_program_button.clicked.connect(self.start_program_clicked.emit)
        self.stop_program_button.clicked.connect(self.stop_program_clicked.emit)

        self._apply_default_settings()

    def _apply_default_settings(self):
        self._set_default_values_for_level("Beginner")

    def _on_level_changed(self, index=0):
        self._set_default_values_for_level(self.level_selector.currentText())

    def _set_default_values_for_level(self, level):
        if level == "Beginner":
            self.hold_time_spin.setValue(20)
            self.repetitions_spin.setValue(1)
        elif level == "Intermediate":
            self.hold_time_spin.setValue(45)
            self.repetitions_spin.setValue(2)
        elif level == "Advanced":
            self.hold_time_spin.setValue(75)
            self.repetitions_spin.setValue(2)

    def get_program_level(self):
        return self.level_selector.currentText()

    def get_hold_time(self):
        return self.hold_time_spin.value()

    def get_rest_time(self):
        return self.rest_time_spin.value()

    def get_repetitions(self):
        return self.repetitions_spin.value()

    def set_program_running(self, running: bool):
        self.start_program_button.setEnabled(not running)
        self.stop_program_button.setEnabled(running)
        if running:
            self.program_status_label.setText("Program status: Running")
        else:
            self.program_status_label.setText("Program status: Idle")

    def update_program_status(self, text: str):
        self.program_status_label.setText(f"Program status: {text}")

    def update_program_timer(self, seconds: int, mode: str = "hold"):
        minutes, secs = divmod(max(0, seconds), 60)
        self.program_timer_label.setText(f"{minutes:02d}:{secs:02d}")
        self.program_timer_label.setProperty("mode", mode)
        self.program_timer_label.style().unpolish(self.program_timer_label)
        self.program_timer_label.style().polish(self.program_timer_label)
        self.program_timer_label.update()

    def reset_program_timer(self):
        self.program_timer_label.setText("00:00")
        self.program_timer_label.setProperty("mode", "hold")
        self.program_timer_label.style().unpolish(self.program_timer_label)
        self.program_timer_label.style().polish(self.program_timer_label)
        self.program_timer_label.update()

    def update_pose(self, pose_name):
        """Update current pose name"""
        self.pose_label.setText(f"Current Pose: {pose_name}")

    def update_image(self, image_path: str, show_next_pose: bool = False):
        """Load and show reference image in the status panel."""
        if not image_path:
            self.image_preview.clear()
            return

        try:
            pix = QPixmap(image_path)
            if pix.isNull():
                self.image_preview.setText("Image not found")
                return

            scaled = pix.scaled(
                self.image_preview.width(),
                self.image_preview.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )

            if show_next_pose:
                result = QPixmap(scaled.size())
                result.fill(Qt.transparent)
                painter = QPainter(result)
                try:
                    painter.drawPixmap(0, 0, scaled)

                    banner_height = max(72, result.height() // 8)
                    painter.fillRect(
                        0, 0, result.width(), banner_height, QColor(0, 0, 0, 180)
                    )
                    painter.setPen(QColor("#4CAF50"))
                    painter.setFont(QFont("Arial", 14, QFont.Bold))
                    painter.drawText(
                        QRect(0, 0, result.width(), banner_height),
                        Qt.AlignCenter,
                        "Next Pose",
                    )
                finally:
                    painter.end()
                self.image_preview.setPixmap(result)
            else:
                self.image_preview.setPixmap(scaled)
        except Exception as e:
            print(f"[ERROR] update_image failed: {e}")
            self.image_preview.setText("Image not found")

    def update_fps(self, fps):
        """Update FPS counter"""
        self.fps_label.setText(f"FPS: {fps:.1f}")

    def update_confidence(self, confidence):
        """Update confidence score (0-100)"""
        self.confidence_label.setText(f"Mediapipe Confidence: {confidence:.1f}%")

    def update_accuracy(self, accuracy):
        """Update pose accuracy (0-100)"""
        self.accuracy_label.setText(f"Pose Matching Accuracy: {accuracy:.1f}%")

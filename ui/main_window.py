from datetime import datetime

from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QFrame,
    QMessageBox,
)
from PyQt5.QtCore import QTimer
import os

from ui.camera_widget import CameraWidget
from ui.pose_selection_panel import PoseSelectionPanel
from ui.instruction_panel import InstructionPanel
from ui.status_panel import StatusPanel
from ui.user_guide_dialog import UserGuideDialog

from core.pose_manager import PoseManager
from ui.styles import get_stylesheet


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "Yoga Pose Assistant"
        )

        

        self.pose_manager = PoseManager()
        self.setStyleSheet(
            get_stylesheet()
        )

        central_widget = QWidget()

        self.setCentralWidget(
            central_widget
        )

        main_layout = QHBoxLayout()

        central_widget.setLayout(
            main_layout
        )

        # ==========================
        # LEFT PANEL
        # ==========================

        self.pose_panel = PoseSelectionPanel()

        main_layout.addWidget(
            self.pose_panel,
            20
        )

        # ==========================
        # CENTER PANEL
        # ==========================

        center_layout = QVBoxLayout()

        main_layout.addLayout(
            center_layout,
            60
        )

        # Camera Widget

        self.camera_widget = CameraWidget()

        center_layout.addWidget(
            self.camera_widget,
            80
        )

        # Instruction Panel

        self.instruction_panel = InstructionPanel()

        center_layout.addWidget(
            self.instruction_panel,
            20
        )

        # ==========================
        # TOOLBAR
        # ==========================

        toolbar = QFrame()

        toolbar_layout = QHBoxLayout()

        toolbar.setLayout(
            toolbar_layout
        )

        self.btn_start = QPushButton(
            "▶ Start Camera"
        )

        self.btn_stop = QPushButton(
            "■ Stop Camera"
        )

        self.btn_capture = QPushButton(
            "📸 Capture"
        )

        self.btn_save = QPushButton(
            "💾 Save"
        )

        self.btn_help = QPushButton(
            "❓ User Guide"
        )

        toolbar_layout.addWidget(
            self.btn_start
        )

        toolbar_layout.addWidget(
            self.btn_stop
        )

        toolbar_layout.addWidget(
            self.btn_capture
        )

        toolbar_layout.addWidget(
            self.btn_save
        )

        toolbar_layout.addWidget(
            self.btn_help
        )

        center_layout.addWidget(
            toolbar
        )

        # ==========================
        # RIGHT PANEL - STATUS
        # ==========================

        self.status_panel = StatusPanel()

        main_layout.addWidget(
            self.status_panel,
            20
        )

        self.program_timer = QTimer(self)
        self.program_timer.timeout.connect(self._advance_program)
        self.countdown_timer = QTimer(self)
        self.countdown_timer.timeout.connect(self._update_countdown)
        self.current_countdown = 0
        self.program_poses = []
        self.program_index = 0
        self.program_rep = 1
        self.program_repetitions = 1
        self.program_running = False
        self.program_resting = False

        # ==========================
        # EVENTS
        # ==========================

        self.btn_start.clicked.connect(
            self.start_camera
        )

        self.btn_stop.clicked.connect(
            self.stop_camera
        )

        self.btn_capture.clicked.connect(
            self.capture_frame
        )

        self.btn_save.clicked.connect(
            self.save_capture
        )

        self.btn_help.clicked.connect(
            self.show_user_guide
        )

        self.pose_panel.pose_selected.connect(
            self.pose_selected
        )

        self.status_panel.start_program_clicked.connect(
            self.start_program
        )
        self.status_panel.stop_program_clicked.connect(
            self.stop_program
        )

        # Connect camera stats to status panel
        self.camera_widget.stats_updated.connect(
            self.on_stats_updated
        )

        # Store current pose name
        self.current_pose_name = "---"

        if UserGuideDialog.should_show_on_startup():
            QTimer.singleShot(300, self._show_startup_guide)

    def _show_startup_guide(self):
        try:
            UserGuideDialog.show_guide(self, show_startup_checkbox=True)
        except Exception as e:
            print(f"[ERROR] Failed to show startup guide: {e}")

    def show_user_guide(self):
        try:
            UserGuideDialog.show_guide(self, show_startup_checkbox=True)
        except Exception as e:
            print(f"[ERROR] Failed to show user guide: {e}")
            QMessageBox.warning(
                self,
                "Guide Error",
                "Unable to open the user guide.",
            )

    def on_stats_updated(self, fps, confidence, accuracy):
        """Update status panel with camera metrics"""
        try:
            self.status_panel.update_fps(fps)
            self.status_panel.update_confidence(confidence)
            self.status_panel.update_accuracy(accuracy)
        except Exception as e:
            print(f"[ERROR] on_stats_updated failed: {e}")

    def start_camera(self):
        try:
            if not self.camera_widget.start_camera():
                QMessageBox.warning(
                    self,
                    "Camera Error",
                    "Unable to open the webcam. Check that a camera is connected and not in use by another app.",
                )
        except Exception as e:
            print(f"[ERROR] start_camera failed: {e}")
            QMessageBox.warning(
                self,
                "Camera Error",
                "An unexpected error occurred while starting the camera.",
            )

    def stop_camera(self):
        try:
            self.camera_widget.stop_camera()
        except Exception as e:
            print(f"[ERROR] stop_camera failed: {e}")

    def capture_frame(self):
        try:
            if not self.camera_widget.capture_frame():
                QMessageBox.warning(
                    self,
                    "Capture Failed",
                    "Start the camera and wait for the live feed before capturing.",
                )
        except Exception as e:
            print(f"[ERROR] capture_frame failed: {e}")
            QMessageBox.warning(
                self,
                "Capture Failed",
                "An unexpected error occurred while capturing the frame.",
            )

    def save_capture(self):
        try:
            if not self.camera_widget.has_captured_image():
                QMessageBox.warning(
                    self,
                    "No Capture",
                    "No image has been captured yet. Please capture a frame first.",
                )
                return

            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            save_dir = os.path.join(project_root, "data", "captured_images")
            os.makedirs(save_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            filename = f"capture_{timestamp}.png"
            save_path = os.path.join(save_dir, filename)

            captured_image = self.camera_widget.get_captured_image()
            if captured_image is None or not captured_image.save(save_path):
                QMessageBox.warning(
                    self,
                    "Save Failed",
                    "Unable to save the captured image.",
                )
                return

            QMessageBox.information(
                self,
                "Saved",
                f"Image saved successfully:\n{save_path}",
            )
        except OSError as e:
            print(f"[ERROR] save_capture failed: {e}")
            QMessageBox.warning(
                self,
                "Save Failed",
                "Unable to create the save folder or write the image file.",
            )
        except Exception as e:
            print(f"[ERROR] save_capture failed: {e}")
            QMessageBox.warning(
                self,
                "Save Failed",
                "An unexpected error occurred while saving the image.",
            )

    def _resolve_pose_image_path(self, pose_name):
        try:
            pose_image_map = {
                "cobra_pose": "Cobra Pose (Bhujangasana).png",
                "downward_dog": "Downward Facing Dog (Adho Mukha Svanasana).png",
                "triangle_pose": "Triangle Pose (Utthita Trikonasana).png",
                "warrior_pose": "Warrior 1 (Virabhadrasana I).png",
                "tree_pose": None,
            }

            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_poses_dir = os.path.join(project_root, "data", "poses")

            mapped = pose_image_map.get(pose_name)
            if mapped:
                candidate = os.path.join(data_poses_dir, mapped)
                if os.path.exists(candidate):
                    return candidate

            for ext in (".png", ".jpg", ".jpeg", ".webp", ".bmp"):
                candidate = os.path.join(data_poses_dir, f"{pose_name}{ext}")
                if os.path.exists(candidate):
                    return candidate
        except Exception as e:
            print(f"[ERROR] _resolve_pose_image_path failed for '{pose_name}': {e}")

        return None

    def _get_next_program_pose_name(self):
        if not self.program_poses:
            return None

        if self.program_rep < self.program_repetitions:
            return self.program_poses[self.program_index]

        next_index = self.program_index + 1
        if next_index < len(self.program_poses):
            return self.program_poses[next_index]

        return None

    def pose_selected(self, pose_name):
        try:
            print(f"[INFO] Selected Pose: {pose_name}")

            self.current_pose_name = pose_name
            self.status_panel.update_pose(pose_name)
            self.status_panel.update_image(self._resolve_pose_image_path(pose_name))

            pose_data = self.pose_manager.load_pose(pose_name)
            if pose_data is None:
                self.instruction_panel.set_instruction("Unable to load pose.")
                return

            self.camera_widget.pose_renderer.set_pose(pose_data)

            instruction_text = self.pose_manager.load_instructions(pose_name)
            if instruction_text:
                self.instruction_panel.set_instruction(instruction_text)
            else:
                self.instruction_panel.set_instruction(
                    f"No instructions available for {pose_name}."
                )
        except Exception as e:
            print(f"[ERROR] pose_selected failed for '{pose_name}': {e}")
            self.instruction_panel.set_instruction("Unable to load pose.")

    def start_program(self):
        try:
            level = self.status_panel.get_program_level()
            self.program_poses = self.pose_panel.get_poses_by_level(level)
            if not self.program_poses:
                self.instruction_panel.set_instruction(
                    f"No {level.lower()} poses available for the program."
                )
                return

            hold_time = self.status_panel.get_hold_time()
            self.program_repetitions = self.status_panel.get_repetitions()
            self.program_index = 0
            self.program_rep = 1
            self.program_running = True
            self.program_resting = False

            self.status_panel.set_program_running(True)
            self.status_panel.update_program_status(
                f"{level} program started ({len(self.program_poses)} poses)"
            )

            self._select_program_pose()
            self._start_phase(hold_time, "hold")
        except Exception as e:
            print(f"[ERROR] start_program failed: {e}")
            self.stop_program()

    def stop_program(self):
        try:
            self.program_timer.stop()
            self.countdown_timer.stop()
            self.program_running = False
            self.program_resting = False
            self.status_panel.set_program_running(False)
            self.status_panel.update_program_status("Stopped")
            self.status_panel.reset_program_timer()
        except Exception as e:
            print(f"[ERROR] stop_program failed: {e}")

    def _select_program_pose(self):
        if self.program_index >= len(self.program_poses):
            self.stop_program()
            self.status_panel.update_program_status("Complete")
            return

        pose_name = self.program_poses[self.program_index]
        self.status_panel.update_program_status(
            f"Hold: {pose_name} ({self.program_rep}/{self.program_repetitions})"
        )
        self.pose_selected(pose_name)

    def _start_phase(self, seconds, mode):
        try:
            self.current_countdown = int(seconds)
            print(f"[DEBUG] Starting phase '{mode}' for {self.current_countdown} seconds")
            self.status_panel.update_program_timer(self.current_countdown, mode)

            if mode == "rest":
                next_pose_name = self._get_next_program_pose_name()
                next_pose_image = (
                    self._resolve_pose_image_path(next_pose_name)
                    if next_pose_name
                    else None
                )
                self.status_panel.update_image(next_pose_image, show_next_pose=True)
                self.camera_widget.pose_renderer.paused = True
            else:
                self.camera_widget.pose_renderer.paused = False

            self.countdown_timer.start(1000)
            self.program_timer.start(int(seconds) * 1000)
        except Exception as e:
            print(f"[ERROR] _start_phase failed: {e}")

    def _update_countdown(self):
        try:
            self.current_countdown -= 1
            if self.current_countdown <= 0:
                self.status_panel.update_program_timer(
                    0, "rest" if self.program_resting else "hold"
                )
                self.countdown_timer.stop()
                print(
                    f"[DEBUG] Countdown reached 0 for "
                    f"{'rest' if self.program_resting else 'hold'} phase"
                )
                return

            mode = "rest" if self.program_resting else "hold"
            self.status_panel.update_program_timer(self.current_countdown, mode)
        except Exception as e:
            print(f"[ERROR] _update_countdown failed: {e}")

    def _advance_program(self):
        if not self.program_running:
            return

        try:
            if self.program_resting:
                self.program_resting = False
                if self.program_rep < self.program_repetitions:
                    self.program_rep += 1
                else:
                    self.program_rep = 1
                    self.program_index += 1

                if self.program_index >= len(self.program_poses):
                    self.stop_program()
                    self.status_panel.update_program_status("Complete")
                    return

                self._select_program_pose()
                hold_time = self.status_panel.get_hold_time()
                self._start_phase(hold_time, "hold")
                return

            if (
                self.program_index == len(self.program_poses) - 1
                and self.program_rep == self.program_repetitions
            ):
                self.stop_program()
                self.status_panel.update_program_status("Complete")
                return

            self.program_resting = True
            rest_time = self.status_panel.get_rest_time()
            self.status_panel.update_program_status(
                f"Resting {rest_time} sec before next pose"
            )
            self._start_phase(rest_time, "rest")
        except Exception as e:
            print(f"[ERROR] _advance_program failed: {e}")
            self.stop_program()

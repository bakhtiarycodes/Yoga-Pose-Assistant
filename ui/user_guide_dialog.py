from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextBrowser,
    QCheckBox,
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QSettings


GUIDE_HTML = """
<h2 style="color:#4CAF50;">Welcome to Yoga Pose Assistant</h2>
<p>This app helps you practice yoga poses using your webcam. It compares your body
position to a reference pose in real time and gives you live feedback.</p>

<h3 style="color:#87CEEB;">Quick Start (5 steps)</h3>
<ol>
<li><b>Select a pose</b> from the list on the left (use tabs: All, Beginner, Intermediate, Advanced).</li>
<li>Click <b>▶ Start Camera</b> to begin the live webcam feed.</li>
<li>Stand in front of the camera so your full body is visible.</li>
<li>Match the <b>gray reference skeleton</b> shown in the video.</li>
<li>Watch your <b>Accuracy</b> and colored landmarks improve as you align your pose.</li>
</ol>

<h3 style="color:#87CEEB;">Screen Layout</h3>
<ul>
<li><b>Left panel</b> — Choose a yoga pose from the list.</li>
<li><b>Center (top)</b> — Live camera view with pose overlays.</li>
<li><b>Center (bottom)</b> — Instructions for the selected pose.</li>
<li><b>Toolbar</b> — Camera controls: Start, Stop, Capture, Save, and Help.</li>
<li><b>Right panel</b> — Status, reference image, metrics, and guided program.</li>
</ul>

<h3 style="color:#87CEEB;">Understanding the Camera View</h3>
<ul>
<li><b>Gray skeleton</b> — Reference pose loaded from the selected yoga pose.</li>
<li><b>Colored skeleton (you)</b> — Your body detected by MediaPipe in real time:
    <ul>
    <li><span style="color:#4CAF50;"><b>Green</b></span> — Landmark matches the reference well.</li>
    <li><span style="color:#FFD700;"><b>Yellow</b></span> — Close, but needs a small adjustment.</li>
    <li><span style="color:#FF6B6B;"><b>Red</b></span> — Far from the reference; adjust that body part.</li>
    </ul>
</li>
</ul>

<h3 style="color:#87CEEB;">Status Panel Metrics</h3>
<ul>
<li><b>FPS</b> — Frames per second (how smoothly the camera is running).</li>
<li><b>Confidence</b> — How clearly MediaPipe detects your body (higher is better).</li>
<li><b>Accuracy</b> — How closely your pose matches the reference (0–100%).</li>
<li><b>Reference image</b> — Example photo of the selected pose for visual guidance.</li>
</ul>

<h3 style="color:#87CEEB;">Camera Buttons</h3>
<ul>
<li><b>▶ Start Camera</b> — Opens the webcam and starts pose detection. Use this after
    capture mode or when you first open the app.</li>
<li><b>■ Stop Camera</b> — Stops the webcam and shows a placeholder. The camera is fully released.</li>
<li><b>📸 Capture</b> — Freezes the current frame (with all skeleton overlays) on screen.
    The live feed and MediaPipe stop until you press Start Camera again.</li>
<li><b>💾 Save</b> — Saves the last captured image to
    <code>data/captured_images/capture_YYYY_MM_DD_HH_MM_SS.png</code>.
    You must capture a frame first.</li>
</ul>

<h3 style="color:#87CEEB;">Guided Yoga Program</h3>
<p>In the right panel, you can run an automatic practice session:</p>
<ol>
<li>Choose a <b>Program Level</b> (Beginner, Intermediate, or Advanced).</li>
<li>Set <b>Hold Time</b> — how long to hold each pose.</li>
<li>Set <b>Rest Time</b> — break between poses.</li>
<li>Set <b>Repetitions</b> — how many times to repeat each pose.</li>
<li>Click <b>Start Program</b>. The app will cycle through poses, show a countdown timer,
    and pause skeleton drawing during rest periods.</li>
<li>Click <b>Stop Program</b> to end the session at any time.</li>
</ol>

<h3 style="color:#87CEEB;">Tips for Best Results</h3>
<ul>
<li>Use good lighting and keep your full body in the frame.</li>
<li>Stand far enough from the camera that your head, arms, and legs are all visible.</li>
<li>Select a pose <i>before</i> or <i>after</i> starting the camera — both work.</li>
<li>Read the instructions panel for proper alignment and breathing cues.</li>
<li>Aim for green landmarks and rising accuracy before capturing your best pose.</li>
</ul>

<p style="color:#AAAAAA;"><i>You can reopen this guide anytime with the <b>❓ User Guide</b> button.</i></p>
"""


class UserGuideDialog(QDialog):
    SETTINGS_KEY = "show_user_guide_on_startup"

    def __init__(self, parent=None, show_startup_checkbox=True):
        super().__init__(parent)
        self.setWindowTitle("User Guide — Yoga Pose Assistant")
        self.setMinimumSize(2000, 1500)
        self.resize(820, 640)
        self.setModal(True)

        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel("📖 User Guide")
        title.setFont(QFont("Arial", 36, QFont.Bold))
        title.setStyleSheet("color: #4CAF50; padding: 4px 0;")
        layout.addWidget(title)

        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)
        self.browser.setHtml(GUIDE_HTML)
        self.browser.setStyleSheet(
            """
            QTextBrowser {
                background-color: #1E1E1E;
                border: 1px solid #2C2C2C;
                border-radius: 10px;
                padding: 16px;
                color: #E8E8E8;
                font-size: 28px;
            }
            """
        )
        layout.addWidget(self.browser)

        bottom = QHBoxLayout()

        self.show_on_startup = QCheckBox("Show this guide when the app opens")
        self.show_on_startup.setChecked(self._should_show_on_startup())
        self.show_on_startup.setVisible(show_startup_checkbox)
        bottom.addWidget(self.show_on_startup)

        bottom.addStretch()

        close_btn = QPushButton("Got it — Let's Start")
        close_btn.setMinimumWidth(180)
        close_btn.clicked.connect(self.accept)
        bottom.addWidget(close_btn)

        layout.addLayout(bottom)

    @classmethod
    def _settings(cls):
        return QSettings("YogaPoseAssistant", "YogaPoseAssistant")

    @classmethod
    def should_show_on_startup(cls):
        try:
            settings = cls._settings()
            if not settings.contains(cls.SETTINGS_KEY):
                return True
            return settings.value(cls.SETTINGS_KEY, True, type=bool)
        except Exception as e:
            print(f"[ERROR] should_show_on_startup failed: {e}")
            return True

    def _should_show_on_startup(self):
        return self.should_show_on_startup()

    def _center_on_screen(self):
        screen = QApplication.primaryScreen()
        if screen is None:
            return

        available = screen.availableGeometry()
        x = available.x() + (available.width() - self.width()) // 2
        y = available.y() + (available.height() - self.height()) // 2
        self.move(x, y)

    def accept(self):
        try:
            if self.show_on_startup.isVisible():
                self._settings().setValue(
                    self.SETTINGS_KEY,
                    self.show_on_startup.isChecked(),
                )
        except Exception as e:
            print(f"[ERROR] Failed to save guide settings: {e}")
        super().accept()

    @classmethod
    def show_guide(cls, parent=None, show_startup_checkbox=True):
        try:
            dialog = cls(parent, show_startup_checkbox=show_startup_checkbox)
            dialog._center_on_screen()
            dialog.exec_()
        except Exception as e:
            print(f"[ERROR] show_guide failed: {e}")
            raise

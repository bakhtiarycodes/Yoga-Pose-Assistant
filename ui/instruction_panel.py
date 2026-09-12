from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from PyQt5.QtGui import QFont

class InstructionPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        label = QLabel("Instructions")
        label.setObjectName("instructionLabel")
        label.setFont(QFont("Arial", 24, weight=QFont.Bold))
        layout.addWidget(label)

        self.text_area = QTextEdit()
        self.text_area.setObjectName("instructionTextArea")
        self.text_area.setReadOnly(True)
        self.text_area.setFont(QFont("Arial", 40))
        layout.addWidget(self.text_area)

    def set_instruction(self, text: str):
        self.text_area.setText(text)

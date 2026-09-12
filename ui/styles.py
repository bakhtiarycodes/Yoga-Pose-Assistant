def get_stylesheet():

    return """

    QMainWindow {
        background-color: #121212;
    }

    QWidget {
        background-color: #121212;
        color: white;
        font-size: 24px;
    }

    QListWidget {
        background-color: #1E1E1E;
        border: 1px solid #2C2C2C;
        border-radius: 12px;
        padding: 10px;
    }

    QListWidget::item {
        padding: 12px;
        border-radius: 8px;
    }

    QListWidget::item:selected {
        background-color: #4CAF50;
        color: white;
    }

    QTabWidget::pane {
        background-color: #1E1E1E;
        border: 1px solid #2C2C2C;
        border-radius: 12px;
        padding: 4px;
    }

    QTabBar::tab {
        background-color: #2A2A2A;
        color: white;
        border: 1px solid #2C2C2C;
        border-bottom: none;
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
        padding: 10px 16px;
        min-width: 120px;
    }

    QTabBar::tab:selected {
        background-color: #4CAF50;
        color: white;
    }

    QTabBar::tab:hover {
        background-color: #3A3A3A;
    }

    QComboBox, QSpinBox {
        background-color: #1E1E1E;
        border: 1px solid #2C2C2C;
        border-radius: 8px;
        padding: 8px;
        color: white;
        min-height: 36px;
    }

    QComboBox QAbstractItemView {
        background-color: #1E1E1E;
        color: white;
        border: 1px solid #2C2C2C;
    }

    QTextEdit {
        background-color: #1E1E1E;
        border: 1px solid #2C2C2C;
        border-radius: 12px;
        padding: 10px;
        font-size: 20px;
    }

    QPushButton {

        background-color: #2A2A2A;

        border: 1px solid #333333;

        border-radius: 10px;

        padding: 10px;

        min-height: 40px;
    }

    QPushButton:hover {

        background-color: #3A3A3A;

    }

    QPushButton:pressed {

        background-color: #4CAF50;

    }

    QLabel#programTimerLabel {
        color: #4CAF50;
        font-size: 100px;
        font-weight: bold;
        qproperty-alignment: AlignCenter;
        margin-top: 12px;
        margin-bottom: 12px;
    }

    QLabel#programTimerLabel[mode="rest"] {
        color: #2196F3;
    }

    QLabel#instructionLabel {
        color: #E8F5E9;
        font-size: 30px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    QTextEdit#instructionTextArea {
        background-color: #121212;
        border: 1px solid #2C2C2C;
        border-radius: 12px;
        color: #E8F5E9;
        font-size: 40px;
        padding: 12px;
    }
    """
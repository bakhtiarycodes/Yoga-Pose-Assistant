import sys

from PyQt5.QtWidgets import QApplication, QMessageBox

from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    try:
        window = MainWindow()
        window.showMaximized()
        return app.exec_()
    except Exception as e:
        print(f"[ERROR] Application failed to start: {e}")
        QMessageBox.critical(
            None,
            "Startup Error",
            "The application failed to start. Please restart and try again.",
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())

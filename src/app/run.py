from PyQt5.QtWidgets import QApplication
from src.app.windows.main_window import MainWindow


def start_app():
    print("run.py is being executed")
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    start_app()

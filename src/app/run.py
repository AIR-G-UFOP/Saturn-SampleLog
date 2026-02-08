from PyQt5.QtWidgets import QApplication
from .windows.main_window import MainWindow


def start_app():
    app = QApplication([])
    main_window = MainWindow()
    main_window.show()
    app.exec()

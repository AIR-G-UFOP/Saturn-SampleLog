import os
from PyQt5 import QtWidgets, QtCore
from ..ui.generated.deletewarningdialog import Ui_WarningDialog
from ..modules.ui_functions import UIFunctions

os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"  # Enables per-screen DPI awareness
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"  # Auto-adjust based on system settings
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


class WarningDialog(QtWidgets.QDialog):
    returnWarning = QtCore.pyqtSignal(bool)

    def __init__(self, bg, parent=None):
        super(WarningDialog, self).__init__(parent)

        self.ui = Ui_WarningDialog()
        self.ui.setupUi(self)
        UIFunctions.uiDefinitions(self)

        self.bg = bg
        self.ui.btn_delete.clicked.connect(self.accept)
        self.ui.btn_cancel.clicked.connect(self.reject)

    def resizeEvent(self, event):
        UIFunctions.resize_grips(self)

    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()

    def showEvent(self, event):
        super().showEvent(event)
        self.setup_position()

    def setup_position(self):
        x = self.bg.pos().x() + self.bg.width() // 2 - self.width() // 2
        y = self.bg.pos().y() + self.bg.height() // 2 - self.height() // 2
        self.move(x, y)
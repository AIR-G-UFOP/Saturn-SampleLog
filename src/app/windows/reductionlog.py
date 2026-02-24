import os
import sys
from PyQt5 import QtCore, QtWidgets, QtGui
from ..ui.generated.reductionwindow import Ui_ReductionWindow
from ..modules.ui_functions import UIFunctions


os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"  # Enables per-screen DPI awareness
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"  # Auto-adjust based on system settings
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


class ReductionWindow(QtWidgets.QMainWindow):
    def __init__(self, reduction_service):
        super(ReductionWindow, self).__init__()

        self.ui = Ui_ReductionWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Log new Data Reduction")
        UIFunctions.uiDefinitions(self)

        self.reductionService = reduction_service

        self.ui.btn_cancel.clicked.connect(lambda: self.close())
        self.ui.closeAppBtn.clicked.connect(lambda: self.close())

    def resizeEvent(self, event):
        UIFunctions.resize_grips(self)

    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()

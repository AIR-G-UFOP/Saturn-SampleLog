import os
import sys
from PyQt5 import QtCore, QtWidgets, QtGui
from ..ui.generated.mainwindow import Ui_MainWindow
from ..modules.ui_functions import UIFunctions
from ..windows.userlog import UserWindow


os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"  # Enables per-screen DPI awareness
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"  # Auto-adjust based on system settings
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Main Window")
        UIFunctions.uiDefinitions(self)

        self.ui.btn_newUser.clicked.connect(self.new_user_log)
        self.userLog = None

    def resizeEvent(self, event):
        UIFunctions.resize_grips(self)

    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()

    def btn_clicked(self):
        sender = self.sender().objectName()
        if sender == "btn_newUser":
            self.new_user_log()

    def new_user_log(self):
        self.userLog = UserWindow()
        self.userLog.UserLogReturn.connect(self.new_user_info)
        self.userLog.show()

    QtCore.pyqtSlot(dict)
    def new_user_info(self, user_info):
        print(user_info)

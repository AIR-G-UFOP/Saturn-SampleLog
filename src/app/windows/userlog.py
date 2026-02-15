import os
import sys
from PyQt5 import QtCore, QtWidgets, QtGui
from ..ui.generated.userwindow import Ui_UserWindow
from ..modules.ui_functions import UIFunctions


os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"  # Enables per-screen DPI awareness
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"  # Auto-adjust based on system settings
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


class UserWindow(QtWidgets.QMainWindow):
    UserLogReturn = QtCore.pyqtSignal(dict)

    def __init__(self):
        super(UserWindow, self).__init__()

        self.ui = Ui_UserWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Log new User")
        UIFunctions.uiDefinitions(self)

        self.ui.btn_loguser.clicked.connect(self.emit_user_information)

    def resizeEvent(self, event):
        UIFunctions.resize_grips(self)

    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()

    def emit_user_information(self):
        user_info = {
            "name": self.ui.lineEdit_name.text(),
            "surname": self.ui.lineEdit_surname.text(),
            "organisation": self.ui.lineEdit_org.text(),
            "email": self.ui.lineEdit_email.text(),
            "phone": self.ui.lineEdit_phone.text(),
            "address": self.ui.textEdit_address.toPlainText()
        }
        self.UserLogReturn.emit(user_info)
        self.status_message()
        self.reset_fields()

    def reset_fields(self):
        self.ui.lineEdit_name.clear()
        self.ui.lineEdit_surname.clear()
        self.ui.lineEdit_org.clear()
        self.ui.lineEdit_email.clear()
        self.ui.lineEdit_phone.clear()
        self.ui.textEdit_address.clear()

    def status_message(self):
        QtCore.QTimer.singleShot(0, lambda: self.ui.label_status.setText(
            "User details submitted. See more information in the Main Window"))
        QtCore.QTimer.singleShot(5000, lambda: self.ui.label_status.setText(""))

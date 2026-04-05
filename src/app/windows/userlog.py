import os
import sys
from PyQt5 import QtCore, QtWidgets, QtGui
from ..ui.generated.userwindow import Ui_UserWindow
from ..modules.ui_functions import UIFunctions
from ..utils.utils import (highlight_invalid_field, clear_highlight_field)


os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"  # Enables per-screen DPI awareness
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"  # Auto-adjust based on system settings
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


class UserWindow(QtWidgets.QMainWindow):
    def __init__(self, user_service):
        super(UserWindow, self).__init__()

        self.ui = Ui_UserWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Log new User")
        UIFunctions.uiDefinitions(self)

        self.userService = user_service

        self.ui.btn_loguser.clicked.connect(self.register_user_information)
        self.ui.btn_cancel.clicked.connect(lambda: self.close())
        self.ui.closeAppBtn.clicked.connect(lambda: self.close())

    def resizeEvent(self, event):
        UIFunctions.resize_grips(self)

    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()

    def validate_fields(self):
        valid = True
        message = False
        required_fields = [self.ui.name, self.ui.surname, self.ui.org, self.ui.email, self.ui.phone, self.ui.address]
        for field in required_fields:
            text = field.text().strip() if isinstance(field, QtWidgets.QLineEdit) else field.toPlainText().strip()
            if not text:
                highlight_invalid_field(field)
                valid = False
                message = True
            else:
                clear_highlight_field(field)
        if message:
            self.status_message("Please fill in all required fields.")

        return valid

    def register_user_information(self):
        if not self.validate_fields():
            return
        user_info = {
            "first_name": self.ui.name.text(),
            "surname": self.ui.surname.text(),
            "org": self.ui.org.text(),
            "email": self.ui.email.text(),
            "phone": self.ui.phone.text(),
            "address": self.ui.address.toPlainText()
        }
        try:
            result = self.userService.addUser(user_info)
            self.reset_fields()
            self.status_message(result)
        except Exception as e:
            self.status_message(e)

    def reset_fields(self):
        self.ui.name.clear()
        self.ui.surname.clear()
        self.ui.org.clear()
        self.ui.email.clear()
        self.ui.phone.clear()
        self.ui.address.clear()

    def status_message(self, message):
        QtCore.QTimer.singleShot(0, lambda: self.ui.label_status.setText(message))
        QtCore.QTimer.singleShot(5000, lambda: self.ui.label_status.setText(""))

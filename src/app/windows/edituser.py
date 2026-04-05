import os
import sys
from PyQt5 import QtCore, QtWidgets, QtGui
from ..ui.generated.edituserdialog import Ui_EditUserDialog
from ..modules.ui_functions import UIFunctions
from ..utils.utils import (highlight_invalid_field, clear_highlight_field)

os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"  # Enables per-screen DPI awareness
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"  # Auto-adjust based on system settings
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


class EditUserWindow(QtWidgets.QDialog):
    dialog_return = QtCore.pyqtSignal()

    def __init__(self, user_service, user_id, bg, parent=None):
        super(EditUserWindow, self).__init__(parent)

        self.ui = Ui_EditUserDialog()
        self.ui.setupUi(self)
        self.setWindowTitle("Edit User information")
        self.setWindowFlags(QtCore.Qt.Dialog)
        UIFunctions.uiDefinitions(self)
        self.bg = bg

        self.userService = user_service
        self.user = self.userService.findUserById(user_id)
        self.user_id = user_id
        self.populate_user_info()

        self.ui.btn_saveuser.clicked.connect(self.edit_user_information)
        self.ui.btn_cancel.clicked.connect(self.dialog_close)
        self.ui.btn_close.clicked.connect(self.dialog_close)

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

    def populate_user_info(self):
        self.ui.name.setText(self.user.first_name)
        self.ui.surname.setText(self.user.surname)
        self.ui.org.setText(self.user.org)
        self.ui.email.setText(self.user.email)
        self.ui.phone.setText(self.user.phone)
        self.ui.address.setPlainText(self.user.address)

    def edit_user_information(self):
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
            result = self.userService.editUser(self.user_id, user_info)
            self.status_message(result)
        except Exception as e:
            print(e)
            self.status_message("Something went wrong.")

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

    def status_message(self, message):
        QtCore.QTimer.singleShot(0, lambda: self.ui.label_status.setText(message))
        QtCore.QTimer.singleShot(5000, lambda: self.ui.label_status.setText(""))

    def dialog_close(self):
        self.dialog_return.emit()
        self.close()
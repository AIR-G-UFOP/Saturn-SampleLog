import os
import sys
from PyQt5 import QtCore, QtWidgets, QtGui
from sqlalchemy.testing.pickleable import User

from ..ui.generated.editsampledialog import Ui_EditSampleDialog
from ..modules.ui_functions import UIFunctions

os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"  # Enables per-screen DPI awareness
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"  # Auto-adjust based on system settings
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


class EditSampleWindow(QtWidgets.QDialog):
    dialog_return = QtCore.pyqtSignal()

    def __init__(self, sample_service, sample_id, user_service):
        super(EditSampleWindow, self).__init__()

        self.ui = Ui_EditSampleDialog()
        self.ui.setupUi(self)
        self.setWindowTitle("Edit Sample information")
        UIFunctions.uiDefinitions(self)

        self.sampleService = sample_service
        self.sample = self.sampleService.findSampleById(sample_id)
        self.sample_id = sample_id
        self.userService = user_service
        self.populate_sample_info()

        self.ui.btn_saveSample.clicked.connect(self.edit_sample_information)
        self.ui.btn_cancel.clicked.connect(self.dialog_close)
        self.ui.closeAppBtn.clicked.connect(self.dialog_close)

    def resizeEvent(self, event):
        UIFunctions.resize_grips(self)

    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()

    def populate_sample_info(self):
        users = self.userService.getAllUsers()
        self.ui.userName.clear()
        self.ui.userName.addItem("Select User", None)
        for user in users:
            user_name = f"{user.first_name} {user.surname}"
            self.ui.userName.addItem(user_name, user.id)
            if user.id == self.sample.user_id:
                self.ui.userName.setCurrentText(user_name)
        self.ui.sampleName.setText(self.sample.name)
        self.ui.sampleDescription.setPlainText(self.sample.description)
        self.ui.status.setText(self.sample.status)
        self.ui.instructions.setText(self.sample.comment)
        self.ui.date.setDate(QtCore.QDate(self.sample.date))
        if self.sample.preparation:
            self.ui.prepYes.setChecked(True)
        else:
            self.ui.prepNo.setChecked(True)

    def edit_sample_information(self):
        if not self.validate_fields():
            return
        sample_info = {
            "name": self.ui.sampleName.text(),
            "description": self.ui.sampleDescription.toPlainText(),
            "user_id": self.ui.userName.currentData(),
            "date": self.ui.date.date().toPyDate(),
            "preparation": self.ui.prepYes.isChecked(),
            "comment": self.ui.instructions.text(),
            "status": self.ui.status.text(),
        }
        try:
            result = self.sampleService.editSample(self.sample_id, sample_info)
            self.status_message(result)
        except Exception as e:
            print(e)
            self.status_message("Something went wrong.")

    def validate_fields(self):
        valid = True
        message = False
        if self.ui.userName.currentText() == "Select User":
            self.highlight_invalid_field(self.ui.userName)
            valid = False
            message = True
        else:
            self.clear_highlight_field(self.ui.userName)
        required_fields = [self.ui.sampleName, self.ui.sampleDescription, self.ui.status]
        if self.ui.prepYes.isChecked():
            required_fields.append(self.ui.instructions)
        for field in required_fields:
            text = field.text().strip() if isinstance(field, QtWidgets.QLineEdit) else field.toPlainText().strip()
            if not text:
                self.highlight_invalid_field(field)
                valid = False
                message = True
            else:
                self.clear_highlight_field(field)

        if message:
            self.status_message("Please fill in all required fields.")

        return valid

    @staticmethod
    def highlight_invalid_field(field):
        field.setStyleSheet("border: 1px solid #FF5555;")

    @staticmethod
    def clear_highlight_field(field):
        field.setStyleSheet("")

    def status_message(self, message):
        QtCore.QTimer.singleShot(0, lambda: self.ui.label_status.setText(message))
        QtCore.QTimer.singleShot(5000, lambda: self.ui.label_status.setText(""))

    def dialog_close(self):
        self.dialog_return.emit()
        self.close()
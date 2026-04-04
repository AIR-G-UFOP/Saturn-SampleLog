import os
import sys
from PyQt5 import QtCore, QtWidgets, QtGui
from sqlalchemy.testing.pickleable import User
from ..ui.generated.editsampledialog import Ui_EditSampleDialog
from ..modules.ui_functions import UIFunctions
from ..config.settings import (PREP_HEIGHT, TIME_ANIMATION)

os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"  # Enables per-screen DPI awareness
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"  # Auto-adjust based on system settings
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


class EditSampleWindow(QtWidgets.QDialog):
    dialog_return = QtCore.pyqtSignal()

    def __init__(self, sample_service, sample_id, user_service, bg, parent=None):
        super(EditSampleWindow, self).__init__(parent)

        self.ui = Ui_EditSampleDialog()
        self.ui.setupUi(self)
        self.setWindowTitle("Edit Sample information")
        UIFunctions.uiDefinitions(self)
        self.bg = bg
        self.ui.date.setDate(QtCore.QDate.currentDate())
        self.ui.startDate.setDate(QtCore.QDate.currentDate())
        self.ui.endDate.setDate(QtCore.QDate.currentDate())

        self.sampleService = sample_service
        self.sample = self.sampleService.findSampleById(sample_id)
        self.sample_id = sample_id
        self.userService = user_service
        self.populate_sample_info()

        self.ui.btn_saveSample.clicked.connect(self.edit_sample_information)
        self.ui.btn_cancel.clicked.connect(self.dialog_close)
        self.ui.btn_close.clicked.connect(self.dialog_close)
        self.ui.prepYes.toggled.connect(self.check_prep_state)

        self.ui.startDate.dateChanged.connect(self.check_status_state)
        self.ui.endDate.dateChanged.connect(self.check_status_state)

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
        self.ui.status.setCurrentText(self.sample.status)
        self.ui.instructions.setText(self.sample.comment)
        self.ui.date.setDate(QtCore.QDate(self.sample.status_date))
        self.ui.startDate.setDate(QtCore.QDate(self.sample.start_date))
        self.ui.endDate.setDate(QtCore.QDate(self.sample.end_date))
        if self.sample.preparation:
            self.ui.prepYes.setChecked(True)
            self.check_prep_state()

    def edit_sample_information(self):
        if not self.validate_fields():
            return
        sample_info = {
            "name": self.ui.sampleName.text(),
            "description": self.ui.sampleDescription.toPlainText(),
            "user_id": self.ui.userName.currentData(),
            "status_date": self.ui.date.date().toPyDate(),
            "start_date": self.ui.startDate.date().toPyDate(),
            "end_date": self.ui.endDate.date().toPyDate(),
            "preparation": self.ui.prepYes.isChecked(),
            "comment": self.ui.instructions.text(),
            "status": self.ui.status.currentText(),
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
        required_fields = [self.ui.sampleName, self.ui.sampleDescription]
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

    def check_prep_state(self):
        if self.ui.prepYes.isChecked():
            self.ui.instructions.setEnabled(True)
            self.ui.startDate.setEnabled(True)
            self.ui.endDate.setEnabled(True)
        else:
            self.ui.instructions.setEnabled(False)
            self.ui.startDate.setEnabled(False)
            self.ui.endDate.setEnabled(False)

    def check_status_state(self):
        start_date = self.ui.startDate.date().toPyDate()
        end_date = self.ui.endDate.date().toPyDate()
        status_date = self.ui.date.date().toPyDate()
        if start_date <= status_date <= end_date:
            self.ui.status.setCurrentText("Preparation in progress...")
        elif start_date > status_date:
            self.ui.status.setCurrentText("Logged in")
        elif end_date < status_date:
            self.ui.status.setCurrentText("Preparation completed")
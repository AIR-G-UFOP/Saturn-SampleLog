import os
import sys
from PyQt5 import QtCore, QtWidgets, QtGui
from ..ui.generated.samplewindow import Ui_SampleWindow
from ..modules.ui_functions import UIFunctions
from ..config.ui_settings import (PREP_HEIGHT, TIME_ANIMATION)
from ..utils.utils import (validate_dates, highlight_invalid_field, clear_highlight_field)


os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"  # Enables per-screen DPI awareness
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"  # Auto-adjust based on system settings
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


class SampleWindow(QtWidgets.QMainWindow):
    def __init__(self, sample_service, user_service):
        super(SampleWindow, self).__init__()

        self.ui = Ui_SampleWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Log new Sample")
        UIFunctions.uiDefinitions(self)
        self.ui.date.setDate(QtCore.QDate.currentDate())
        self.ui.startDate.setDate(QtCore.QDate.currentDate())
        self.ui.endDate.setDate(QtCore.QDate.currentDate())

        self.sampleService = sample_service
        self.userService = user_service

        self.animation = QtCore.QPropertyAnimation(self.ui.bgPrepBottom, b"maximumHeight")
        self.animation.setDuration(TIME_ANIMATION)

        self.ui.btn_cancel.clicked.connect(lambda: self.close())
        self.ui.closeAppBtn.clicked.connect(lambda: self.close())
        self.ui.btn_logSample.clicked.connect(self.register_sample_information)
        self.ui.prepYes.toggled.connect(self.check_prep_state)
        self.ui.startDate.dateChanged.connect(self.check_status_state)
        self.ui.endDate.dateChanged.connect(self.check_status_state)

        self.load_users()

    def resizeEvent(self, event):
        UIFunctions.resize_grips(self)

    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()

    def load_users(self):
        users = self.userService.getAllUsers()
        self.ui.userName.clear()
        self.ui.userName.addItem("Select User", None)
        for user in users:
            user_name = f"{user.first_name} {user.surname}"
            self.ui.userName.addItem(user_name, user.id)

    def validate_fields(self):
        valid = True
        message = False
        if self.ui.userName.currentText() == "Select User":
            highlight_invalid_field(self.ui.userName)
            valid = False
            message = True
        else:
            clear_highlight_field(self.ui.userName)
        required_fields = [self.ui.sampleName, self.ui.sampleDescription]
        if self.ui.prepYes.isChecked():
            required_fields.append(self.ui.instructions)
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

    def register_sample_information(self):
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
            "status": self.ui.status.currentText()
        }
        try:
            result = self.sampleService.addSample(sample_info)
            self.reset_fields()
            self.status_message(result)
        except Exception as e:
            self.status_message('Something went wrong. See logs for details.')
            raise

    def reset_fields(self):
        self.ui.sampleName.clear()
        self.ui.sampleDescription.clear()
        self.ui.userName.setCurrentIndex(0)
        self.ui.date.clear()
        self.ui.endDate.clear()
        self.ui.startDate.clear()
        self.ui.status.setCurrentIndex(0)
        self.ui.prepYes.setChecked(False)
        self.ui.instructions.clear()

    def status_message(self, message):
        QtCore.QTimer.singleShot(0, lambda: self.ui.label_status.setText(message))
        QtCore.QTimer.singleShot(5000, lambda: self.ui.label_status.setText(""))

    def check_prep_state(self):
        if self.ui.prepYes.isChecked():
            self.animation.setStartValue(0)
            self.animation.setEndValue(PREP_HEIGHT)
        else:
            self.animation.setStartValue(PREP_HEIGHT)
            self.animation.setEndValue(0)
        self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.animation.start()

    def check_status_state(self):
        sender = self.sender()
        start_date = self.ui.startDate.date().toPyDate()
        end_date = self.ui.endDate.date().toPyDate()
        status_date = self.ui.date.date().toPyDate()
        if validate_dates(start_date, end_date):
            if start_date <= status_date <= end_date:
                self.ui.status.setCurrentText("Preparation in progress...")
            elif start_date > status_date:
                self.ui.status.setCurrentText("Logged in")
            elif end_date < status_date:
                self.ui.status.setCurrentText("Preparation completed")
            clear_highlight_field(sender)
        else:
            self.status_message("Please select a valid date. The end date must be after the start date.")
            highlight_invalid_field(sender)

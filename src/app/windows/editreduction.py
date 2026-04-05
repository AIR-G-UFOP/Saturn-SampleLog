import os
import sys
from PyQt5 import QtCore, QtWidgets, QtGui
from ..modules.ui_functions import UIFunctions
from ..ui.generated.editreductiondialog import Ui_EditeReductionWindow
from ..utils.utils import validate_dates

os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"  # Enables per-screen DPI awareness
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"  # Auto-adjust based on system settings
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


class EditReductionWindow(QtWidgets.QDialog):
    dialog_return = QtCore.pyqtSignal()

    def __init__(self, reduction_service, reduction_id, analysis_service, bg, parent=None):
        super(EditReductionWindow, self).__init__(parent)

        self.ui = Ui_EditeReductionWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Edit Reduction information")
        UIFunctions.uiDefinitions(self)
        self.bg = bg
        self.ui.date.setDate(QtCore.QDate.currentDate())
        self.ui.startEnd.setDate(QtCore.QDate.currentDate())
        self.ui.endDate.setDate(QtCore.QDate.currentDate())

        self.reductionService = reduction_service
        self.reduction = self.reductionService.getReductionById(reduction_id)
        self.reduction_id = reduction_id
        self.analysisService = analysis_service

        self.populate_reduction_info()
        self.ui.btn_saveReduction.clicked.connect(self.edit_reduction_information)
        self.ui.btn_cancel.clicked.connect(self.dialog_close)
        self.ui.btn_close.clicked.connect(self.dialog_close)
        self.ui.startEnd.dateChanged.connect(self.check_status_state)
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

    def dialog_close(self):
        self.dialog_return.emit()
        self.close()

    def status_message(self, message):
        QtCore.QTimer.singleShot(0, lambda: self.ui.label_status.setText(message))
        QtCore.QTimer.singleShot(5000, lambda: self.ui.label_status.setText(""))

    @staticmethod
    def highlight_invalid_field(field):
        field.setStyleSheet("border: 1px solid #FF5555;")

    @staticmethod
    def clear_highlight_field(field):
        field.setStyleSheet("")

    def populate_reduction_info(self):
        analyses = self.analysisService.getAllAnalyses()
        self.ui.analysis.clear()
        self.ui.analysis.addItem("Select Analysis", None)
        for analysis in analyses:
            name = f"{analysis.method}-{analysis.status_date.strftime('%Y-%m-%d')}"
            self.ui.analysis.addItem(name, analysis.id)
            if self.reduction_id == analysis.id:
                self.ui.analysis.setCurrentText(name)
        self.ui.reductionName.setText(self.reduction.reduction_name)
        self.ui.software.setText(self.reduction.software)
        self.ui.version.setText(self.reduction.software_version)
        self.ui.handler.setText(self.reduction.handler)
        self.ui.notes.setPlainText(self.reduction.notes)
        self.ui.status.setCurrentText(self.reduction.status)
        self.ui.date.setDate(QtCore.QDate(self.reduction.status_date))
        self.ui.startEnd.setDate(QtCore.QDate(self.reduction.start_date))
        self.ui.endDate.setDate(QtCore.QDate(self.reduction.end_date))
        self.ui.file.setText(self.reduction.file_name)
        if self.reduction.file_name != "":
            self.ui.generate.setChecked(True)

    def validate_fields(self):
        valid = True
        message = False
        if self.ui.analysis.currentText() == "Select User":
            self.highlight_invalid_field(self.ui.analysis)
            valid = False
            message = True
        else:
            self.clear_highlight_field(self.ui.analysis)
        required_fields = [self.ui.reductionName, self.ui.software, self.ui.version, self.ui.handler, self.ui.notes]
        if not self.ui.generate.isChecked():
            required_fields.append(self.ui.file)
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

    def edit_reduction_information(self):
        if not self.validate_fields():
            return
        reduction_info = {
            "reduction_name": self.ui.reductionName.text(),
            "software": self.ui.software.text(),
            "version": self.ui.version.text(),
            "handler": self.ui.handler.text(),
            "status_date": self.ui.date.date().toPyDate(),
            "start_date": self.ui.startEnd.date().toPyDate(),
            "end_date": self.ui.endDate.date().toPyDate(),
            "notes": self.ui.notes.toPlainText(),
            "file_name": self.ui.file.text(),
            "analysis_id": self.ui.analysis.currentData(),
            "status": self.ui.status.currentText(),
        }
        try:
            result = self.reductionService.editReduction(self.reduction_id, reduction_info)
            self.status_message(result)
        except:
            self.status_message("An error occurred. Please try again.")
            raise

    def check_status_state(self):
        sender = self.sender()
        start_date = self.ui.startEnd.date().toPyDate()
        end_date = self.ui.endDate.date().toPyDate()
        status_date = self.ui.date.date().toPyDate()
        if validate_dates(start_date, end_date):
            if start_date <= status_date <= end_date:
                self.ui.status.setCurrentText("Data Reduction in progress...")
            elif start_date > status_date:
                self.ui.status.setCurrentText("Logged in")
            elif end_date < status_date:
                self.ui.status.setCurrentText("Data Reduction finished")
            self.clear_highlight_field(sender)
        else:
            self.status_message("Please select a valid date. The end date must be after the start date.")
            self.highlight_invalid_field(sender)

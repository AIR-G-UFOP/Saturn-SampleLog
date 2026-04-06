import os
import sys
from PyQt5 import QtCore, QtWidgets, QtGui
from ..ui.generated.reductionwindow import Ui_ReductionWindow
from ..modules.ui_functions import UIFunctions
from ..utils.utils import (validate_dates, highlight_invalid_field, clear_highlight_field)
from ..modules.file_name_generator import FileNameGenerator


os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"  # Enables per-screen DPI awareness
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"  # Auto-adjust based on system settings
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


class ReductionWindow(QtWidgets.QMainWindow):
    def __init__(self, reduction_service, analysis_service, settings_service):
        super(ReductionWindow, self).__init__()

        self.ui = Ui_ReductionWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Log new Data Reduction")
        UIFunctions.uiDefinitions(self)
        self.ui.date.setDate(QtCore.QDate.currentDate())
        self.ui.startDate.setDate(QtCore.QDate.currentDate())
        self.ui.endDate.setDate(QtCore.QDate.currentDate())

        self.reductionService = reduction_service
        self.analysisService = analysis_service
        self.settingsService = settings_service

        self.ui.btn_cancel.clicked.connect(lambda: self.close())
        self.ui.closeAppBtn.clicked.connect(lambda: self.close())
        self.ui.btn_logReduction.clicked.connect(self.register_reduction_information)
        self.ui.startDate.dateChanged.connect(self.check_status_state)
        self.ui.endDate.dateChanged.connect(self.check_status_state)
        self.ui.generate.toggled.connect(self.generate_file_name)
        self.ui.reductionName.textChanged.connect(self.generate_file_name)
        self.ui.handler.textChanged.connect(self.generate_file_name)
        self.ui.date.dateChanged.connect(self.generate_file_name)
        self.ui.btn_copy.clicked.connect(self.copy_file_name_to_clipboard)

        self.load_analysis()

    def resizeEvent(self, event):
        UIFunctions.resize_grips(self)

    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()

    def load_analysis(self):
        analyses = self.analysisService.getAllAnalyses()
        self.ui.analysis.clear()
        self.ui.analysis.addItem("Select Analysis", None)
        for anal in analyses:
            analysis_name = f"{anal.method}-{anal.status_date.strftime('%Y%m%d')}"
            self.ui.analysis.addItem(analysis_name, anal.id)

    def validate_fields(self):
        valid = True
        message = False
        if self.ui.analysis.currentText() == "Select User":
            highlight_invalid_field(self.ui.analysis)
            valid = False
            message = True
        else:
            clear_highlight_field(self.ui.analysis)
        required_fields = [self.ui.reductionName, self.ui.software, self.ui.version, self.ui.handler, self.ui.notes_2]
        if not self.ui.generate.isChecked():
            required_fields.append(self.ui.fileName)
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

    def reset_fields(self):
        self.ui.analysis.clear()
        self.ui.software.clear()
        self.ui.version.clear()
        self.ui.reductionName.clear()
        self.ui.handler.clear()
        self.ui.fileName.clear()
        self.ui.notes.clear()
        self.ui.date.clear()
        self.ui.status.setCurrentIndex(0)
        self.ui.generate.setChecked(False)
        self.ui.date.setDate(QtCore.QDate.currentDate())
        self.ui.startDate.setDate(QtCore.QDate.currentDate())
        self.ui.endDate.setDate(QtCore.QDate.currentDate())
        self.ui.notes.clear()

    def register_reduction_information(self):
        if not self.validate_fields():
            return
        reduction_info = {
            "reduction_name": self.ui.reductionName.text(),
            "software": self.ui.software.text(),
            "version": self.ui.version.text(),
            "handler": self.ui.handler.text(),
            "status_date": self.ui.date.date().toPyDate(),
            "start_date": self.ui.startDate.date().toPyDate(),
            "end_date": self.ui.endDate.date().toPyDate(),
            "notes": self.ui.notes_2.toPlainText(),
            "file_name": self.ui.fileName.text(),
            "analysis_id": self.ui.analysis.currentData(),
            "status": self.ui.status.currentText(),
            "generate_file_name": self.ui.generate.isChecked()
        }
        try:
            result = self.reductionService.addReduction(reduction_info)
            self.reset_fields()
            self.status_message(result)
        except:
            self.status_message("Error logging data reduction")
            raise

    def status_message(self, message):
        QtCore.QTimer.singleShot(0, lambda: self.ui.label_status.setText(message))
        QtCore.QTimer.singleShot(5000, lambda: self.ui.label_status.setText(""))

    def check_status_state(self):
        sender = self.sender()
        start_date = self.ui.startDate.date().toPyDate()
        end_date = self.ui.endDate.date().toPyDate()
        status_date = self.ui.date.date().toPyDate()
        if validate_dates(start_date, end_date):
            if start_date <= status_date <= end_date:
                self.ui.status.setCurrentText("Data Reduction in progress...")
            elif start_date > status_date:
                self.ui.status.setCurrentText("Logged in")
            elif end_date < status_date:
                self.ui.status.setCurrentText("Data Reduction finished")
            clear_highlight_field(self.ui.startDate)
            clear_highlight_field(self.ui.endDate)
        else:
            self.status_message("Please select a valid date. The end date must be after the start date.")
            highlight_invalid_field(sender)

    def generate_file_name(self):
        if self.ui.generate.isChecked():
            file_name_config = self.settingsService.getFileNameSettings()
            template = file_name_config["template"]
            separator = file_name_config["separator"]
            fragments = []
            for frag in template:
                if frag == "Current date":
                    fragments.append(QtCore.QDate.currentDate().toString("yyyyMMdd"))
                elif frag == "Status date":
                    fragments.append(self.ui.date.date().toString("yyyyMMdd"))
                elif frag == "Analysis/Reduction name":
                    fragments.append(self.ui.reductionName.text())
                elif frag == "Operator/Handler name":
                    fragments.append(self.ui.handler.text())
                else:
                    fragments.append(frag)
            if fragments:
                gen = FileNameGenerator(fragments, separator)
                self.ui.fileName.setText(gen.generate())
        else:
            if self.ui.fileName.text() == "":
                self.ui.fileName.clear()

    def copy_file_name_to_clipboard(self):
        if self.ui.fileName.text() != "":
            file_name = self.ui.fileName.text()
            clipboard = QtWidgets.QApplication.clipboard()
            clipboard.setText(file_name)
            self.ui.btn_copy.setIcon(QtGui.QIcon(u":/icons/icons/cill-ok-filled.png"))
            QtCore.QTimer.singleShot(2000,
                lambda: self.ui.btn_copy.setIcon(QtGui.QIcon(u":/icons/icons/cil-copy.png")))

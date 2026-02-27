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
    def __init__(self, reduction_service, analysis_service):
        super(ReductionWindow, self).__init__()

        self.ui = Ui_ReductionWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Log new Data Reduction")
        UIFunctions.uiDefinitions(self)

        self.reductionService = reduction_service
        self.analysisService = analysis_service

        self.ui.btn_cancel.clicked.connect(lambda: self.close())
        self.ui.closeAppBtn.clicked.connect(lambda: self.close())
        self.ui.btn_logReduction.clicked.connect(self.register_reduction_information)

        self.load_analysis()

    def resizeEvent(self, event):
        UIFunctions.resize_grips(self)

    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()

    def load_analysis(self):
        analyses = self.analysisService.getAllAnalyses()
        self.ui.analysis.clear()
        self.ui.analysis.addItem("Select User", None)
        for anal in analyses:
            analysis_name = f"{anal.method}-{anal.date.strftime('%Y-%m-%d')}"
            self.ui.analysis.addItem(analysis_name, anal.id)

    def validate_fields(self):
        valid = True
        message = False
        if self.ui.analysis.currentText() == "Select User":
            self.highlight_invalid_field(self.ui.analysis)
            valid = False
            message = True
        else:
            self.clear_highlight_field(self.ui.analysis)
        required_fields = [self.ui.reductionName, self.ui.software, self.ui.version, self.ui.handler, self.ui.notes_2]
        if not self.ui.generate.isChecked():
            required_fields.append(self.ui.fileName)
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

    def reset_fields(self):
        self.ui.analysis.clear()
        self.ui.software.clear()
        self.ui.version.clear()
        self.ui.reductionName.clear()
        self.ui.handler.clear()
        self.ui.fileName.clear()
        self.ui.notes.clear()
        self.ui.date.clear()

    def register_reduction_information(self):
        if not self.validate_fields():
            return
        reduction_info = {
            "reduction_name": self.ui.reductionName.text(),
            "software": self.ui.software.text(),
            "version": self.ui.version.text(),
            "handler": self.ui.handler.text(),
            "date": self.ui.date.date().toPyDate(),
            "notes": self.ui.notes_2.toPlainText(),
            "file_id": self.ui.fileName.text(),
            "analysis_id": self.ui.analysis.currentData()
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

    @staticmethod
    def highlight_invalid_field(field):
        field.setStyleSheet("border: 1px solid #FF5555;")

    @staticmethod
    def clear_highlight_field(field):
        field.setStyleSheet("")
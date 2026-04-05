import os
import sys
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtGui import QStandardItem
from ..ui.generated.analysiswindow import Ui_AnalysisWindow
from ..modules.ui_functions import UIFunctions
from ..utils.utils import validate_dates


os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"  # Enables per-screen DPI awareness
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"  # Auto-adjust based on system settings
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


class AnalysisWindow(QtWidgets.QMainWindow):
    def __init__(self, analysis_service, sample_service):
        super(AnalysisWindow, self).__init__()

        self.ui = Ui_AnalysisWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Log new Analysis")
        UIFunctions.uiDefinitions(self)
        self.ui.date.setDate(QtCore.QDate.currentDate())
        self.ui.startDate.setDate(QtCore.QDate.currentDate())
        self.ui.endDate.setDate(QtCore.QDate.currentDate())

        self.analysisService = analysis_service
        self.sampleService = sample_service

        self.ui.btn_cancel.clicked.connect(lambda: self.close())
        self.ui.closeAppBtn.clicked.connect(lambda: self.close())
        self.ui.btn_logAnalysis.clicked.connect(self.register_analysis_information)
        self.ui.startDate.dateChanged.connect(self.check_status_state)
        self.ui.endDate.dateChanged.connect(self.check_status_state)

        self.load_samples()

    def resizeEvent(self, event):
        UIFunctions.resize_grips(self)

    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()

    def load_samples(self):
        samples = self.sampleService.getAllSamples()
        combo = self.ui.sample
        model = QtGui.QStandardItemModel(combo)
        combo.setModel(model)
        combo.setEditable(True)
        combo.lineEdit().setReadOnly(True)
        combo.lineEdit().setText("Select Sample(s)")
        combo.lineEdit().setStyleSheet("""background: transparent; border: none;""")
        combo.lineEdit().setFocusPolicy(QtCore.Qt.NoFocus)
        for smp in samples:
            item = QStandardItem(smp.name)
            item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable)
            item.setData(QtCore.Qt.Unchecked, QtCore.Qt.CheckStateRole)
            item.setData(smp.id, QtCore.Qt.UserRole)
            model.appendRow(item)
        combo.setCurrentIndex(-1)
        combo.lineEdit().clear()
        combo.lineEdit().setPlaceholderText("Select Sample(s)")
        model.itemChanged.connect(lambda: self.update_combobox_text(combo))

    def update_combobox_text(self, combo):
        checked_items = self.get_checked_items(combo)
        if not checked_items:
            combo.lineEdit().clear()
            return
        if len(checked_items) <=3:
            combo.lineEdit().setText(", ".join(checked_items))
        else:
            combo.lineEdit().setText(f"{len(checked_items)} samples selected")

    def register_analysis_information(self):
        if not self.validate_fields():
            return
        analysis_info = {
            "method": self.ui.analysisName.text(),
            "equipment": self.ui.equipment.text(),
            "status_date": self.ui.date.date().toPyDate(),
            "start_date": self.ui.startDate.date().toPyDate(),
            "end_date": self.ui.endDate.date().toPyDate(),
            "operator": self.ui.operator_2.text(),
            "conditions": self.ui.analysisNotes.toPlainText(),
            "file_name": self.ui.fileName.text(),
            "status": self.ui.status.currentText(),
        }
        sample_ids = self.get_checked_data(self.ui.sample)
        try:
            result = self.analysisService.addAnalysis(analysis_info, sample_ids)
            self.reset_fields()
            self.status_message(result)
        except Exception as e:
            self.status_message("Something went wrong. Check log for details.")
            raise

    def validate_fields(self):
        valid = True
        message = False
        if len(self.get_checked_data(self.ui.sample)) == 0:
            self.highlight_invalid_field(self.ui.sample)
            valid = False
            message = True
        else:
            self.clear_highlight_field(self.ui.sample)
        required_fields = [self.ui.analysisName, self.ui.equipment, self.ui.operator_2,self.ui.analysisNotes]
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

    @staticmethod
    def get_checked_items(combo):
        model = combo.model()
        items = []
        for i in range(model.rowCount()):
            item = model.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                items.append(item.text())
        return items

    @staticmethod
    def get_checked_data(combo):
        model = combo.model()
        data_list = []
        for i in range(model.rowCount()):
            item = model.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                data_list.append(item.data(QtCore.Qt.UserRole))
        return data_list

    def reset_fields(self):
        self.ui.analysisName.clear()
        self.ui.equipment.clear()
        self.ui.operator_2.clear()
        self.ui.analysisNotes.clear()
        self.ui.fileName.clear()
        for i in range(self.ui.sample.model().rowCount()):
            item = self.ui.sample.model().item(i)
            item.setCheckState(QtCore.Qt.Unchecked)
        self.ui.generate.setChecked(False)

    def status_message(self, message):
        QtCore.QTimer.singleShot(0, lambda: self.ui.label_status.setText(message))
        QtCore.QTimer.singleShot(5000, lambda: self.ui.label_status.setText(""))

    @staticmethod
    def highlight_invalid_field(field):
        field.setStyleSheet("border: 1px solid #FF5555;")

    @staticmethod
    def clear_highlight_field(field):
        field.setStyleSheet("")

    def check_status_state(self):
        sender = self.sender()
        start_date = self.ui.startDate.date().toPyDate()
        end_date = self.ui.endDate.date().toPyDate()
        status_date = self.ui.date.date().toPyDate()
        if validate_dates(start_date, end_date):
            if start_date <= status_date <= end_date:
                self.ui.status.setCurrentText("Analysis in progress...")
            elif start_date > status_date:
                self.ui.status.setCurrentText("Logged in")
            elif end_date < status_date:
                self.ui.status.setCurrentText("Analysis completed")
            self.clear_highlight_field(sender)
        else:
            self.status_message("Please select a valid date. The end date must be after the start date.")
            self.highlight_invalid_field(sender)
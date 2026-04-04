import os
import sys
from PyQt5 import QtCore, QtWidgets, QtGui
from sqlalchemy.testing.pickleable import User
from ..modules.ui_functions import UIFunctions
from ..ui.generated.editanalysisdialog import Ui_EditAnalysisWindow

os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"  # Enables per-screen DPI awareness
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"  # Auto-adjust based on system settings
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


class EditAnalysisWindow(QtWidgets.QDialog):
    dialog_return = QtCore.pyqtSignal()

    def __init__(self, analysis_service, analysis_id, sample_service, bg, parent=None):
        super(EditAnalysisWindow, self).__init__(parent)

        self.ui = Ui_EditAnalysisWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Edit Analysis information")
        UIFunctions.uiDefinitions(self)
        self.bg = bg
        self.ui.date.setDate(QtCore.QDate.currentDate())
        self.ui.startDate.setDate(QtCore.QDate.currentDate())
        self.ui.endDate.setDate(QtCore.QDate.currentDate())

        self.analysisService = analysis_service
        self.analysis = self.analysisService.findAnalysisById(analysis_id)
        self.analysis_id = analysis_id
        self.sampleService = sample_service
        self.populate_analysis_information()

        self.ui.btn_saveAnalysis.clicked.connect(self.edit_analysis_information)
        self.ui.btn_cancel.clicked.connect(self.dialog_close)
        self.ui.btn_close.clicked.connect(self.dialog_close)
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
            item = QtGui.QStandardItem(smp.name)
            item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable)
            for selected_smp in self.analysis.samples:
                if smp.id == selected_smp.id:
                    item.setData(QtCore.Qt.Checked, QtCore.Qt.CheckStateRole)
                else:
                    item.setData(QtCore.Qt.Unchecked, QtCore.Qt.CheckStateRole)
            item.setData(smp.id, QtCore.Qt.UserRole)
            model.appendRow(item)
        combo.setCurrentIndex(-1)
        combo.lineEdit().clear()
        combo.lineEdit().setPlaceholderText("Select Sample(s)")
        model.itemChanged.connect(lambda: self.update_combobox_text(combo))
        self.update_combobox_text(combo)

    def update_combobox_text(self, combo):
        checked_items = self.get_checked_items(combo)
        if not checked_items:
            combo.lineEdit().clear()
            return
        if len(checked_items) <= 3:
            combo.lineEdit().setText(", ".join(checked_items))
        else:
            combo.lineEdit().setText(f"{len(checked_items)} samples selected")

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

    def populate_analysis_information(self):
        self.load_samples()
        self.ui.analysisName.setText(self.analysis.method)
        self.ui.equipment.setText(self.analysis.equipment)
        self.ui.operator_2.setText(self.analysis.operator)
        self.ui.analysisNotes.setPlainText(self.analysis.conditions)
        self.ui.fileName.setText(self.analysis.file_name)
        self.ui.status.setCurrentText(self.analysis.status)
        self.ui.date.setDate(QtCore.QDate(self.analysis.status_date))
        self.ui.startDate.setDate(QtCore.QDate(self.analysis.start_date))
        self.ui.endDate.setDate(QtCore.QDate(self.analysis.end_date))
        if self.analysis.file_name != "":
            self.ui.generate.setChecked(True)

    def edit_analysis_information(self):
        if not self.validate_fields():
            return
        analysis_info = {
            "method": self.ui.analysisName.text(),
            "equipment": self.ui.equipment.text(),
            "operator": self.ui.operator_2.text(),
            "conditions": self.ui.analysisNotes.toPlainText(),
            "status_date": self.ui.date.date().toPyDate(),
            "start_date": self.ui.startDate.date().toPyDate(),
            "end_date": self.ui.endDate.date().toPyDate(),
            "status": self.ui.status.currentText(),
            "file_name": self.ui.fileName.text(),
        }
        sample_ids = self.get_checked_data(self.ui.sample)
        try:
            result = self.analysisService.editAnalysis(self.analysis_id, analysis_info, sample_ids)
            self.status_message(result)
        except Exception as e:
            print(e)
            self.status_message("Something went wrong.")

    def validate_fields(self):
        valid = True
        message = False
        if len(self.get_checked_data(self.ui.sample)) == 0:
            self.highlight_invalid_field(self.ui.sample)
            valid = False
            message = True
        else:
            self.clear_highlight_field(self.ui.sample)
        required_fields = [self.ui.analysisName, self.ui.equipment, self.ui.operator_2, self.ui.analysisNotes]
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

    def check_status_state(self):
        start_date = self.ui.startDate.date().toPyDate()
        end_date = self.ui.endDate.date().toPyDate()
        status_date = self.ui.date.date().toPyDate()

        if start_date <= status_date <= end_date:
            self.ui.status.setCurrentText("Analysis in progress...")
        elif start_date > status_date:
            self.ui.status.setCurrentText("Logged in")
        elif end_date < status_date:
            self.ui.status.setCurrentText("Analysis completed")

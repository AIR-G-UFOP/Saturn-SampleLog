import os
from PyQt5 import QtWidgets, QtCore
from ..ui.generated.addtaskdialog import Ui_AddTaskDialog
from ..modules.ui_functions import UIFunctions
from ..utils.utils import (highlight_invalid_field, clear_highlight_field, validate_dates)


os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"  # Enables per-screen DPI awareness
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"  # Auto-adjust based on system settings
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

class AddTaskDialog(QtWidgets.QDialog):
    returnAddTask = QtCore.pyqtSignal()

    def __init__(self, sample_service, analysis_service, reduction_service, task_service, parent, bg, date):
        super(AddTaskDialog, self).__init__(parent)

        self.ui = Ui_AddTaskDialog()
        self.ui.setupUi(self)
        self.setWindowTitle("Add New Task")
        self.setWindowFlags(QtCore.Qt.Dialog)
        UIFunctions.uiDefinitions(self)
        self.bg = bg

        self.taskService = task_service
        self.sampleService = sample_service
        self.analysisService = analysis_service
        self.reductionService = reduction_service

        self.ui.startDate.setDate(date)
        self.ui.endDate.setDate(QtCore.QDate.currentDate())
        self.check_type()
        self.load_samples()
        self.load_analyses()
        self.load_reductions()

        self.ui.btn_close.clicked.connect(self.dialog_close)
        self.ui.btn_cancel.clicked.connect(self.dialog_close)
        self.ui.btn_add.clicked.connect(self.add_task)
        self.ui.taskType.currentIndexChanged.connect(self.check_type)

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

    def load_samples(self):
        samples = self.sampleService.getAllSamples()
        self.ui.samples.addItem("Select Sample")
        for smp in samples:
            self.ui.samples.addItem(smp.name, userData=smp.id)

    def load_analyses(self):
        analyses = self.analysisService.getAllAnalyses()
        self.ui.analysis.addItem("Select Analysis")
        for aan in analyses:
            self.ui.analysis.addItem(aan.method, userData=aan.id)

    def load_reductions(self):
        reductions = self.reductionService.getAllReductions()
        self.ui.reduction.addItem("Select Reduction")
        for red in reductions:
            self.ui.reduction.addItem(red.reduction_name, userData=red.id)

    def check_type(self):
        task_type = self.ui.taskType.currentText()
        if task_type == "Sample preparation":
            self.ui.samples.setEnabled(True)
            self.ui.analysis.setEnabled(False)
            self.ui.reduction.setEnabled(False)
        elif task_type == "Analysis":
            self.ui.analysis.setEnabled(True)
            self.ui.samples.setEnabled(False)
            self.ui.reduction.setEnabled(False)
        elif task_type == "Data reduction":
            self.ui.reduction.setEnabled(True)
            self.ui.samples.setEnabled(False)
            self.ui.analysis.setEnabled(False)
        else:
            self.ui.samples.setEnabled(False)
            self.ui.analysis.setEnabled(False)
            self.ui.reduction.setEnabled(False)

    def check_date(self):
        start_date = self.ui.startDate.date()
        end_date = self.ui.endDate.date()
        if validate_dates(start_date, end_date):
            for widget in [self.ui.startDate, self.ui.endDate]:
                clear_highlight_field(widget)
                return True
        else:
            self.status_message("Please select a valid date. The end date must be after the start date.")
            for widget in [self.ui.startDate, self.ui.endDate]:
                highlight_invalid_field(widget)
                return False

    def get_id(self):
        task_type = self.ui.taskType.currentText()
        if task_type == "Sample preparation":
            return "sample_id", self.ui.samples.currentData()
        elif task_type == "Analysis":
            return "analysis_id", self.ui.analysis.currentData()
        elif task_type == "Data reduction":
            return "reduction_id", self.ui.reduction.currentData()
        else:
            return None, None

    def validate_fields(self):
        valid = True
        message = False
        required_fields = [self.ui.name, self.ui.description]
        task_type = self.ui.taskType.currentText()
        if task_type == "Sample preparation":
            if self.ui.samples.currentText() == "Select Sample":
                message = True
                valid = False
                highlight_invalid_field(self.ui.samples)
        elif task_type == "Analysis":
            if self.ui.analysis.currentText() == "Select Analysis":
                message = True
                valid = False
                highlight_invalid_field(self.ui.analysis)
        elif task_type == "Data reduction":
            if self.ui.reduction.currentText() == "Select Reduction":
                message = True
                valid = False
                highlight_invalid_field(self.ui.reduction)
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
        self.ui.name.clear()
        self.ui.description.clear()
        self.ui.samples.setCurrentIndex(0)
        self.ui.analysis.setCurrentIndex(0)
        self.ui.reduction.setCurrentIndex(0)
        self.ui.startDate.setDateTime(QtCore.QDateTime.currentDateTime())
        self.ui.endDate.setDateTime(QtCore.QDateTime.currentDateTime())

    def status_message(self, message):
        QtCore.QTimer.singleShot(0, lambda: self.ui.label_status.setText(message))
        QtCore.QTimer.singleShot(5000, lambda: self.ui.label_status.setText(""))

    def add_task(self):
        if not self.validate_fields() or not self.check_date():
            return
        task_type = self.ui.taskType.currentText()
        if task_type == "Sample preparation":
            t_type = "sample_preparation"
        elif task_type == "Analysis":
            t_type = "analysis"
        elif task_type == "Data reduction":
            t_type = "reduction"
        else:
            t_type = "other"
        task_info = {
            "name": f"{self.ui.name.text()}",
            "start_date": self.ui.startDate.date().toPyDate(),
            "end_date": self.ui.endDate.date().toPyDate(),
            "status": "Pending",
            "description": self.ui.description.text(),
            "task_type": t_type,
        }
        parent_name, parent_id = self.get_id()
        if parent_name:
            task_info["parent_name"] = parent_id
        try:
            self.taskService.upsertTask(task_info)
            self.reset_fields()
            self.status_message("Task added successfully.")
        except Exception as e:
            self.status_message("An error occurred while adding task.")
            raise

    def dialog_close(self):
        self.returnAddTask.emit()
        self.close()

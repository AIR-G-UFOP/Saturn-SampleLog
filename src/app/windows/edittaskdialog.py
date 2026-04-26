import os
from PyQt5 import QtCore, QtWidgets
from ..ui.generated.edittaskdialog import Ui_EditTaskDialog
from ..modules.ui_functions import UIFunctions
from ..utils.utils import (highlight_invalid_field, clear_highlight_field, validate_dates)
from ..widgets.overlay import LoadingOverlay
from .warningdialog import WarningDialog


os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"  # Enables per-screen DPI awareness
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"  # Auto-adjust based on system settings
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


class EditTaskDialog(QtWidgets.QDialog):
    returnEditTask = QtCore.pyqtSignal()

    def __init__(self, parent, bg, task, sample_service, analysis_service, reduction_service, task_service):
        super(EditTaskDialog, self).__init__(parent)

        self.ui = Ui_EditTaskDialog()
        self.ui.setupUi(self)
        self.setWindowTitle("Edit Task")
        self.setWindowFlags(QtCore.Qt.Dialog)
        UIFunctions.uiDefinitions(self)
        self.bg = bg
        self.overlay = LoadingOverlay(self.ui.bgApp)
        self.overlay.hide()

        self.task = task
        self.sampleService = sample_service
        self.analysisService = analysis_service
        self.reductionService = reduction_service
        self.taskService = task_service
        self.completed = False

        self.ui.startDate.setDate(self.task.start_date)
        self.ui.endDate.setDate(self.task.end_date)
        self.ui.name.setText(self.task.name)
        self.ui.description.setText(self.task.description)
        self.set_task_parent()
        self.set_task_type()

        self.ui.btn_close.clicked.connect(self.dialog_close)
        self.ui.btn_delete.clicked.connect(self.delete_task)
        self.ui.btn_edit.clicked.connect(self.edit_task)

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

    def set_task_type(self):
        task_type = self.task.task_type
        if task_type == "sample_preparation":
            self.ui.taskType.setText("Sample Preparation")
        elif task_type == "analysis":
            self.ui.taskType.setText("Analysis")
        elif task_type == "reduction":
            self.ui.taskType.setText("Reduction")
        else:
            self.ui.taskType.setText("Other")

    def set_task_parent(self):
        task_type = self.task.task_type
        if task_type == "other":
            self.ui.parent.setText("None")
            return
        if task_type == "sample_preparation":
            sample_id = self.task.sample_id
            sample = self.sampleService.findSampleById(sample_id)
            self.ui.parent.setText(f"{sample.name}")
        elif task_type == "analysis":
            analysis_id = self.task.analysis_id
            analysis = self.analysisService.findAnalysisById(analysis_id)
            self.ui.parent.setText(f"{analysis.method}")
        elif task_type == "reduction":
            reduction_id = self.task.reduction_id
            reduction = self.reductionService.getReductionById(reduction_id)
            self.ui.parent.setText(f"{reduction.reduction_name}")

    def validate_fields(self):
        valid = True
        message = False
        required_fields = [self.ui.name, self.ui.description]
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

    def validate_dates(self):
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

    def edit_task(self):
        if not self.validate_fields() or not self.validate_dates():
            return
        task_info = {
            "id": self.task.id,
            "name": self.ui.name.text(),
            "description": self.ui.description.text(),
            "status": self.ui.status.currentText(),
            "start_date": self.ui.startDate.date().toPyDate(),
            "end_date": self.ui.endDate.date().toPyDate(),
            "task_type": self.task.task_type,
        }
        if self.ui.status == "Completed":
            task_info["completed_at"] = QtCore.QDate.currentDate().toPyDate()
            self.completed = True
        try:
            self.taskService.upsertTask(task_info)
            if self.completed:
                self.handle_parent_status()
            self.status_message("Task updated successfully.")
        except Exception as e:
            self.status_message("An error occurred while updating the task.")
            raise

    def delete_task(self):
        self.overlay.show()
        dialog = WarningDialog(self.ui.bgApp, self)
        dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        result = dialog.exec()
        self.overlay.hide()
        if result:
            self.taskService.deleteTask(self.task.id)
            self.remove_task_from_parent()
            self.dialog_close()

    def handle_parent_status(self):
        task_type = self.task.task_type
        if task_type == "other":
            return
        if task_type == "sample_preparation":
            sample_id = self.task.sample_id
            self.sampleService.updateStatus(sample_id, "Preparation completed", QtCore.QDate.currentDate().toPyDate())
        elif task_type == "analysis":
            analysis_id = self.task.analysis_id
            self.analysisService.updateStatus(analysis_id, "Analysis completed", QtCore.QDate.currentDate().toPyDate())
        elif task_type == "reduction":
            reduction_id = self.task.reduction_id
            self.reductionService.updateStatus(reduction_id, "Data Reduction finished",
                                               QtCore.QDate.currentDate().toPyDate())

    def remove_task_from_parent(self):
        task_type = self.task.task_type
        if task_type == "other":
            return
        if task_type == "sample_preparation":
            sample_id = self.task.sample_id
            self.sampleService.removeTask(sample_id)
        elif task_type == "analysis":
            analysis_id = self.task.analysis_id
            self.analysisService.removeTask(analysis_id)
        elif task_type == "reduction":
            reduction_id = self.task.reduction_id
            self.reductionService.removeTask(reduction_id)

    def status_message(self, message):
        QtCore.QTimer.singleShot(0, lambda: self.ui.label_status.setText(message))
        QtCore.QTimer.singleShot(5000, lambda: self.ui.label_status.setText(""))

    def dialog_close(self):
        self.returnEditTask.emit()
        self.close()


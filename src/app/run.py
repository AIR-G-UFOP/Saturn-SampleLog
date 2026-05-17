from PyQt5.QtWidgets import QApplication


from src.app.windows.mainwindow import MainWindow
from src.app.services.user_service import UserService
from src.app.services.sample_service import SampleService
from src.app.services.analysis_service import AnalysisService
from src.app.services.reduction_service import ReductionService
from src.app.services.settings_service import SettingsService
from src.app.services.task_service import TaskService
from src.app.services.notebook_service import NotebookService
from src.app.services.logbook_service import LogbookService
import sys
import traceback


def excepthook(type_, value, tb):
    traceback.print_exception(type_, value, tb)

sys.excepthook = excepthook


def start_app():
    user_service = UserService()
    sample_service = SampleService()
    analysis_service = AnalysisService()
    reduction_service = ReductionService()
    settings_service = SettingsService()
    task_service = TaskService()
    notebook_service = NotebookService()
    logbook_service = LogbookService()
    app = QApplication([])
    window = MainWindow(user_service, sample_service, analysis_service, reduction_service, settings_service,
                        task_service, notebook_service, logbook_service)
    window.show()
    app.exec()


if __name__ == "__main__":
    start_app()

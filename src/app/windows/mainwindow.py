import os
import sys
from PyQt5 import QtCore, QtWidgets, QtGui
from ..ui.generated.mainwindow import Ui_MainWindow
from ..modules.ui_functions import UIFunctions
from ..windows.userlog import UserWindow
from ..windows.samplelog import SampleWindow
from ..windows.analysislog import AnalysisWindow
from ..windows.reductionlog import ReductionWindow

os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"  # Enables per-screen DPI awareness
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"  # Auto-adjust based on system settings
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, user_service, sample_service, analysis_service, reduction_service):
        super(MainWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Main Window")
        UIFunctions.uiDefinitions(self)

        self.userService = user_service
        self.sampleService = sample_service
        self.analysisService = analysis_service
        self.reductionService = reduction_service

        self.ui.btn_newUser.clicked.connect(self.btn_clicked)
        self.ui.btn_newSample.clicked.connect(self.btn_clicked)
        self.ui.btn_newAnalysis.clicked.connect(self.btn_clicked)
        self.ui.btn_newReduction.clicked.connect(self.btn_clicked)
        self.ui.closeAppBtn.clicked.connect(lambda: self.close())
        self.userLog = None

    def resizeEvent(self, event):
        UIFunctions.resize_grips(self)

    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()

    def btn_clicked(self):
        sender = self.sender().objectName()
        if sender == "btn_newUser":
            self.open_user_log()
        elif sender == "btn_newSample":
            self.open_sample_log()
        elif sender == "btn_newAnalysis":
            self.open_analysis_log()
        elif sender == "btn_newReduction":
            self.open_reduction_log()

    def open_user_log(self):
        self.userLog = UserWindow(self.userService)
        self.userLog.show()

    def open_sample_log(self):
        self.sampleLog = SampleWindow(self.sampleService)
        self.sampleLog.show()

    def open_analysis_log(self):
        self.analysisLog = AnalysisWindow(self.analysisService)
        self.analysisLog.show()

    def open_reduction_log(self):
        self.reductionLog = ReductionWindow(self.reductionService)
        self.reductionLog.show()
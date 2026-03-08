import os
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from ..modules.ui_functions import UIFunctions
from ..ui.generated.listwindow import Ui_ListWindow

os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"  # Enables per-screen DPI awareness
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"  # Auto-adjust based on system settings
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


class DbListWindow(QtWidgets.QMainWindow):
    def __init__(self, db_type):
        super(DbListWindow, self).__init__()

        self.setWindowTitle("Database List Window")
        self.ui = Ui_ListWindow()
        self.ui.setupUi(self)
        UIFunctions.uiDefinitions(self)
        self.ui.toggleButton.clicked.connect(lambda: UIFunctions.toggleMenu(self, True))

        self.dbType = db_type

        self.ui.closeAppBtn.clicked.connect(lambda: self.close())
        self.ui.btn_userList.clicked.connect(self.btn_clicked)
        self.ui.btn_sampleList.clicked.connect(self.btn_clicked)
        self.ui.btn_analysisList.clicked.connect(self.btn_clicked)
        self.ui.btn_reductionList.clicked.connect(self.btn_clicked)
        self.ui.btn_addUser.clicked.connect(self.btn_clicked)
        self.ui.btn_addSample.clicked.connect(self.btn_clicked)
        self.ui.btn_addAnalysis.clicked.connect(self.btn_clicked)
        self.ui.btn_addReductions.clicked.connect(self.btn_clicked)
        self.ui.btn_settings.clicked.connect(self.btn_clicked)

    def resizeEvent(self, event):
        UIFunctions.resize_grips(self)

    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()

    def btn_clicked(self):
        btn = self.sender()
        btn_name = btn.objectName()
        UIFunctions.resetStyle(self, btn_name)
        btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))
        if btn_name == "btn_userList":
            self.ui.contentStack.setCurrentWidget(self.ui.lists)
            self.dbType = "user"
        elif btn_name == "btn_sampleList":
            self.ui.contentStack.setCurrentWidget(self.ui.lists)
            self.dbType = "sample"
        elif btn_name == "btn_analysisList":
           self.ui.contentStack.setCurrentWidget(self.ui.lists)
           self.dbType = "analysis"
        elif btn_name == "btn_reductionList":
            self.ui.contentStack.setCurrentWidget(self.ui.lists)
            self.dbType = "reduction"
        elif btn_name == "btn_addUser":
            pass
        elif btn_name == "btn_addSample":
            pass
        elif btn_name == "btn_addAnalysis":
            pass
        elif btn_name == "btn_addReductions":
            pass
        elif btn_name == "btn_settings":
            self.ui.contentStack.setCurrentWidget(self.ui.settings)

    def load_cards(self):
        # Clear existing cards

        # Load cards based on db list type
        if self.dbType == "user":
            pass
        elif self.dbType == "sample":
            pass
        elif self.dbType == "analysis":
            pass
        elif self.dbType == "reduction":
            pass

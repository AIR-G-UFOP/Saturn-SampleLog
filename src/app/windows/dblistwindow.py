import os
from PyQt5 import QtWidgets, QtCore, QtGui

from ..modules.ui_functions import UIFunctions
from ..ui.generated.listwindow import Ui_ListWindow
from ..widgets.usercard import UserCard
from ..widgets.samplecard import SampleCard
from ..widgets.analysiscard import AnalysisCard
from ..widgets.reductioncard import ReductionCard
from ..widgets.overlay import LoadingOverlay
from .edituser import EditUserWindow
from .editsample import EditSampleWindow
from .editanalysis import EditAnalysisWindow
from .editreduction import EditReductionWindow
from .appsettings import Settings


os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"  # Enables per-screen DPI awareness
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"  # Auto-adjust based on system settings
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


class DbListWindow(QtWidgets.QMainWindow):
    def __init__(self, db_type, user_service, sample_service, analysis_service, reduction_service, settings_service):
        super(DbListWindow, self).__init__()

        self.setWindowTitle("Database List Window")
        self.ui = Ui_ListWindow()
        self.ui.setupUi(self)
        UIFunctions.uiDefinitions(self)
        self.ui.toggleButton.clicked.connect(lambda: UIFunctions.toggleMenu(self, True))
        self.ui.panelArea.setWidgetResizable(True)
        self.ui.bgCardsLayout.addStretch()
        self.ui.bgCardsLayout.setAlignment(QtCore.Qt.AlignTop)

        self.dbType = db_type
        self.userService = user_service
        self.sampleService = sample_service
        self.analysisService = analysis_service
        self.reductionService = reduction_service
        self.settingsService = settings_service
        self.overlay = LoadingOverlay(self.ui.bgApp)
        self.overlay.hide()
        self.settings = Settings(self.ui, self.settingsService)

        self.DATA_MAP = {
            "user": (self.userService.getAllUsersFull, UserCard),
            "sample": (self.sampleService.getAllSamplesFull, SampleCard),
            "analysis": (self.analysisService.getAllAnalysesFull, AnalysisCard),
            "reduction": (self.reductionService.getAllReductionsFull, ReductionCard)
        }
        BUTTON_DB_MAP = {
            "user": self.ui.btn_userList,
            "sample": self.ui.btn_sampleList,
            "analysis": self.ui.btn_analysisList,
            "reduction": self.ui.btn_reductionList
        }
        self.cards = []

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
        self.ui.listFrag.model().rowsMoved.connect(self.update_file_name_preview)

        self.set_btn_style(BUTTON_DB_MAP[self.dbType],
                           BUTTON_DB_MAP[self.dbType].objectName())
        self.load_cards()

    def resizeEvent(self, event):
        UIFunctions.resize_grips(self)

    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()

    def btn_clicked(self):
        btn = self.sender()
        btn_name = btn.objectName()
        self.set_btn_style(btn, btn_name)
        if btn_name == "btn_userList":
            self.ui.contentStack.setCurrentWidget(self.ui.lists)
            self.dbType = "user"
            self.load_cards()
        elif btn_name == "btn_sampleList":
            self.ui.contentStack.setCurrentWidget(self.ui.lists)
            self.dbType = "sample"
            self.load_cards()
        elif btn_name == "btn_analysisList":
           self.ui.contentStack.setCurrentWidget(self.ui.lists)
           self.dbType = "analysis"
           self.load_cards()
        elif btn_name == "btn_reductionList":
            self.ui.contentStack.setCurrentWidget(self.ui.lists)
            self.dbType = "reduction"
            self.load_cards()
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

    def set_btn_style(self, btn, btn_name):
        UIFunctions.resetStyle(self, btn_name)
        btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

    @QtCore.pyqtSlot(object)
    def card_clicked(self, selected_card):
        for card in self.cards:
            if card == selected_card:
                card.check_card_state()
            else:
                card.collapse()

    def clear_cards(self):
        while self.ui.bgCardsLayout.count() > 1:
            item = self.ui.bgCardsLayout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.cards.clear()

    def load_cards(self):
        self.clear_cards()
        loader, card_class = self.DATA_MAP[self.dbType]
        data = loader()
        for obj in data:
            card = card_class(obj)
            self.add_card(card)
            card.clicked.connect(self.card_clicked)
            card.edit_requested.connect(self.open_edit_dialog)
            self.cards.append(card)

    def add_card(self, card):
        self.ui.bgCardsLayout.insertWidget(self.ui.bgCardsLayout.count() - 1, card)

    @QtCore.pyqtSlot(str, int)
    def open_edit_dialog(self, db_type, db_id):
        db_type_map = {
            "user": EditUserWindow(self.userService, db_id, self.ui.bgApp, self),
            "sample": EditSampleWindow(self.sampleService, db_id, self.userService, self.ui.bgApp, self),
            "analysis": EditAnalysisWindow(self.analysisService, db_id, self.sampleService, self.settingsService,
                                           self.ui.bgApp, self),
            "reduction": EditReductionWindow(self.reductionService, db_id, self.analysisService, self.ui.bgApp, self),
        }
        self.overlay.show()
        dialog = db_type_map[db_type]
        dialog.dialog_return.connect(self.return_edit_dialog)
        dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        dialog.exec_()

    @QtCore.pyqtSlot()
    def return_edit_dialog(self):
        self.overlay.hide()
        self.load_cards()

    def update_file_name_preview(self):
        pass
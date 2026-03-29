from PyQt5 import QtCore, QtGui, QtWidgets
from ..ui.generated.usercard import Ui_UserCardWidget
from ..config.settings import (CARD_MIN_HEIGHT, USER_DETAILS_HEIGHT, WIDGET_INFO_HEIGHT,
                               WIDGET_INFO_STYLESHEET, CARD_SUBHEADING_STYLESHEET, LABEL_COLOUR,
                               CARD_BUTTON_ICON_DOWN, CARD_BUTTON_ICON_UP)


class UserCard(QtWidgets.QWidget):
    clicked = QtCore.pyqtSignal(object)
    edit_requested = QtCore.pyqtSignal(str, int)

    def __init__(self, user):
        super(UserCard, self).__init__()
        self.ui = Ui_UserCardWidget()
        self.ui.setupUi(self)

        self.user_id = user.id

        self.ui.userTitle.setText(f"{user.first_name} {user.surname}")
        self.ui.org.setText(f"{user.org}")
        self.ui.address.setText(f"{user.address}")
        self.ui.phone.setText(f"{user.phone}")
        self.ui.email.setText(f"{user.email}")

        self.sample_number = 0
        self.analyses_number = 0
        self.reductions_number = 0

        self.sample_info(user.samples)
        self.ui.analysisTitle.setText(f"{self.analyses_number} Analyses")
        self.ui.reductionTitle.setText(f"{self.reductions_number} Reductions")
        self.added_info = max(self.sample_number, self.analyses_number, self.reductions_number)

        self.ui.btn_edit.clicked.connect(self.edit_user)
        self.ui.btn_toggle.clicked.connect(self.trigger_card_stated_change)

    def check_card_state(self):
        if self.ui.bgCard.height() == CARD_MIN_HEIGHT:
            self.expand()
        else:
            self.collapse()

    def expand(self):
        if self.added_info > 2:
            increase = 184
        else:
            increase = 88 * self.added_info + 10 * (self.added_info - 1)
        self.ui.bgUserDetails.setMaximumHeight(USER_DETAILS_HEIGHT)
        self.ui.bgBottom.setMaximumHeight(65 + increase)
        self.ui.bgSampleBottom.setMaximumHeight(increase)
        self.ui.bgAnalysisBottom.setMaximumHeight(increase)
        self.ui.bgReductionBottom.setMaximumHeight(increase)
        self.ui.btn_toggle.setIcon(QtGui.QIcon(CARD_BUTTON_ICON_UP))

    def collapse(self):
        if self.ui.bgCard.height() != CARD_MIN_HEIGHT:
            self.ui.bgUserDetails.setMaximumHeight(0)
            self.ui.bgBottom.setMaximumHeight(0)
            self.ui.bgSampleBottom.setMaximumHeight(0)
            self.ui.bgAnalysisBottom.setMaximumHeight(0)
            self.ui.bgReductionBottom.setMaximumHeight(0)
            self.ui.btn_toggle.setIcon(QtGui.QIcon(CARD_BUTTON_ICON_DOWN))

    def create_info_widget(self, info_name, info_status, info_date):
        bgInfo = QtWidgets.QFrame(self)
        bgInfo.setMaximumHeight(WIDGET_INFO_HEIGHT)
        bgInfo.setMinimumHeight(WIDGET_INFO_HEIGHT)
        bgInfo.setProperty("role", "card")
        bgInfo.setStyleSheet(WIDGET_INFO_STYLESHEET)
        vLayout = QtWidgets.QVBoxLayout(bgInfo)
        name = QtWidgets.QLabel(self)
        name.setText(info_name)
        name.setStyleSheet(CARD_SUBHEADING_STYLESHEET)
        status = QtWidgets.QLabel(self)
        status.setText(f"Status: {info_status}")
        status.setStyleSheet(LABEL_COLOUR)
        date = QtWidgets.QLabel(self)
        date.setText(info_date.strftime("%d-%m-%Y"))
        date.setStyleSheet(LABEL_COLOUR)
        vLayout.addWidget(name)
        vLayout.addWidget(status)
        vLayout.addWidget(date)
        return bgInfo

    def sample_info(self, samples):
        self.ui.sampleTitle.setText(f"{len(samples)} Samples")
        self.sample_number = len(samples)
        for sample in samples:
            bgInfo = self.create_info_widget(sample.name, sample.status, sample.date)
            self.ui.sampleLayout.addWidget(bgInfo)
            self.analysis_info(sample.analyses)

    def analysis_info(self, analyses):
        self.analyses_number += len(analyses)
        for analysis in analyses:
            bgInfo = self.create_info_widget(analysis.method, analysis.status, analysis.date)
            self.ui.AnalysisLayout.addWidget(bgInfo)
            self.reduction_info(analysis.reduction)

    def reduction_info(self, reduction):
        if reduction:
            self.reductions_number += 1
            bgInfo = self.create_info_widget(reduction.reduction_name, reduction.status, reduction.date)
            self.ui.reductionLayout.addWidget(bgInfo)

    def edit_user(self):
        self.edit_requested.emit("user", self.user_id)

    def trigger_card_stated_change(self):
        self.clicked.emit(self)
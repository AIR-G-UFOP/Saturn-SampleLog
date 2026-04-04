from PyQt5 import QtCore, QtGui, QtWidgets
from ..ui.generated.analysiscard import Ui_AnalysisCardWidget
from ..config.settings import (CARD_MIN_HEIGHT, ANALYSIS_DETAILS_HEIGHT, CARD_BUTTON_ICON_UP,
                               CARD_BUTTON_ICON_DOWN, WIDGET_INFO_STYLESHEET, WIDGET_INFO_HEIGHT,
                               CARD_SUBHEADING_STYLESHEET, LABEL_COLOUR, FILE_LABEL_COLOUR)


class AnalysisCard(QtWidgets.QWidget):
    clicked = QtCore.pyqtSignal(object)
    edit_requested = QtCore.pyqtSignal(str, int)

    def __init__(self, analysis):
        super(AnalysisCard, self).__init__()
        self.ui = Ui_AnalysisCardWidget()
        self.ui.setupUi(self)
        self.setMouseTracking(True)
        self.ui.bgCard.setMouseTracking(True)

        self.analysis_id = analysis.id

        self.users_number = 0
        self.reductions_number = 0
        self.sample_number = 0
        self.previous_user = None

        self.ui.analysisTitle.setText(analysis.method)
        self.ui.equipment.setText(f"Equipment: {analysis.equipment}")
        self.ui.operator_.setText(f"Operator: {analysis.operator}")
        self.ui.conditions.setText(f"Conditions: {analysis.conditions}")
        self.ui.status.setText(f"Status: {analysis.status}")
        self.ui.date.setText(analysis.status_date.strftime('%Y-%m-%d'))
        self.ui.file.setText(f"Saved as: {analysis.file_name}")
        self.ui.file.setStyleSheet(FILE_LABEL_COLOUR)
        self.samples_info(analysis.samples)
        self.reduction_info(analysis.reduction)

        self.ui.userTitle.setText(f"{self.users_number} Users")
        self.ui.reductionTitle.setText(f"{self.reductions_number} Reductions")
        self.added_info = max(self.users_number, self.reductions_number, self.sample_number)

        self.ui.btn_edit.clicked.connect(self.edit_analysis)
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
        self.ui.bgAnalysisDetails.setMaximumHeight(ANALYSIS_DETAILS_HEIGHT)
        self.ui.bgBottom.setMaximumHeight(65 + increase)
        self.ui.bgUserBottom.setMaximumHeight(increase)
        self.ui.bgSampleBottom.setMaximumHeight(increase)
        self.ui.bgReductionBottom.setMaximumHeight(increase)
        self.ui.btn_toggle.setIcon(QtGui.QIcon(CARD_BUTTON_ICON_UP))

    def collapse(self):
        if self.ui.bgCard.height() != CARD_MIN_HEIGHT:
            self.ui.bgAnalysisDetails.setMaximumHeight(0)
            self.ui.bgBottom.setMaximumHeight(0)
            self.ui.bgUserBottom.setMaximumHeight(0)
            self.ui.bgSampleBottom.setMaximumHeight(0)
            self.ui.bgReductionBottom.setMaximumHeight(0)
            self.ui.btn_toggle.setIcon(QtGui.QIcon(CARD_BUTTON_ICON_DOWN))

    def create_info_widget(self, info_name, info_status, info_date, info_org):
        bgInfo = QtWidgets.QFrame(self)
        bgInfo.setMaximumHeight(WIDGET_INFO_HEIGHT)
        bgInfo.setMinimumHeight(WIDGET_INFO_HEIGHT)
        bgInfo.setProperty("role", "card")
        bgInfo.setStyleSheet(WIDGET_INFO_STYLESHEET)
        vLayout = QtWidgets.QVBoxLayout(bgInfo)
        name = QtWidgets.QLabel(self)
        name.setText(info_name)
        name.setStyleSheet(CARD_SUBHEADING_STYLESHEET)
        vLayout.addWidget(name)
        if info_status is not None:
            status = QtWidgets.QLabel(self)
            status.setText(f"Status: {info_status}")
            status.setStyleSheet(LABEL_COLOUR)
            vLayout.addWidget(status)
        if info_date is not None:
            date = QtWidgets.QLabel(self)
            date.setText(info_date.strftime("%d-%m-%Y"))
            date.setStyleSheet(LABEL_COLOUR)
            vLayout.addWidget(date)
        if info_org is not None:
            org = QtWidgets.QLabel(self)
            org.setText(info_org)
            org.setStyleSheet(LABEL_COLOUR)
            vLayout.addWidget(org)
            vLayout.addItem(QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        return bgInfo

    def samples_info(self, samples):
        self.ui.sampleTitle.setText(f"{len(samples)} Samples")
        self.sample_number = len(samples)
        for sample in samples:
            bgInfo = self.create_info_widget(sample.name, sample.status, sample.status_date, None)
            self.ui.sampleLayout.addWidget(bgInfo)
            self.user_info(sample.users)

    def user_info(self, user):
        if self.previous_user != user.id:
            self.users_number += 1
            bgInfo = self.create_info_widget(f"{user.first_name} {user.surname}", None, None,
                                             user.org)
            self.ui.userLayout.addWidget(bgInfo)
            self.previous_user = user.id

    def reduction_info(self, reduction):
        if reduction:
            self.reductions_number += 1
            bgInfo = self.create_info_widget(reduction.reduction_name, reduction.status, reduction.status_date, None)
            self.ui.reductionLayout.addWidget(bgInfo)

    def edit_analysis(self):
        self.edit_requested.emit("analysis", self.analysis_id)

    def trigger_card_stated_change(self):
        self.clicked.emit(self)
from PyQt5 import QtCore, QtGui, QtWidgets
from ..ui.generated.samplecard import Ui_SampleCardWidget
from ..config.ui_settings import (CARD_MIN_HEIGHT, SAMPLE_DETAILS_HEIGHT, CARD_BUTTON_ICON_UP,
                                  CARD_BUTTON_ICON_DOWN, WIDGET_INFO_HEIGHT, WIDGET_INFO_STYLESHEET,
                                  CARD_SUBHEADING_STYLESHEET, LABEL_COLOUR, SAMPLE_STATUS_COLOUR, ANALYSIS_STATUS_COLOUR,
                                  REDUCTION_STATUS_COLOUR)


class SampleCard(QtWidgets.QWidget):
    clicked = QtCore.pyqtSignal(object)
    edit_requested = QtCore.pyqtSignal(str, int)

    def __init__(self, sample):
        super(SampleCard, self).__init__()
        self.ui = Ui_SampleCardWidget()
        self.ui.setupUi(self)
        self.setMouseTracking(True)
        self.ui.bgCard.setMouseTracking(True)

        self.sample_id = sample.id
        self.reductions_number = 0
        self.analysis_number = 0

        self.ui.sampleTitle.setText(f"{sample.name}")
        self.ui.description.setText(f"{sample.description}")
        self.ui.status.setText(f"Status: {sample.status}")
        self.ui.status.setStyleSheet(SAMPLE_STATUS_COLOUR[sample.status])
        self.ui.date.setText(f"{sample.status_date.strftime('%Y-%m-%d')}")
        self.ui.prep.setText(f"Preparation: {sample.preparation}")
        self.ui.comment.setText(f"Comment: {sample.comment}")
        self.user_info(sample.users)
        self.analyses_info(sample.analyses)

        self.ui.reductionTitle.setText(f"{self.reductions_number} Reductions")
        self.ui.userTitle.setText(f"User")
        self.added_info = max(self.reductions_number, self.analysis_number)

        self.ui.btn_edit.clicked.connect(self.edit_sample)
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
        self.ui.bgSampleDetails.setMaximumHeight(SAMPLE_DETAILS_HEIGHT)
        self.ui.bgBottom.setMaximumHeight(65 + increase)
        self.ui.bgUserBottom.setMaximumHeight(increase)
        self.ui.bgAnalysisBottom.setMaximumHeight(increase)
        self.ui.bgReductionBottom.setMaximumHeight(increase)
        self.ui.btn_toggle.setIcon(QtGui.QIcon(CARD_BUTTON_ICON_UP))

    def collapse(self):
        if self.ui.bgCard.height() != CARD_MIN_HEIGHT:
            self.ui.bgSampleDetails.setMaximumHeight(0)
            self.ui.bgBottom.setMaximumHeight(0)
            self.ui.bgUserBottom.setMaximumHeight(0)
            self.ui.bgAnalysisBottom.setMaximumHeight(0)
            self.ui.bgReductionBottom.setMaximumHeight(0)
            self.ui.btn_toggle.setIcon(QtGui.QIcon(CARD_BUTTON_ICON_DOWN))

    def create_info_widget(self, info_name, info_status, info_date, info_org, status_colour):
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
            status.setStyleSheet(status_colour)
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

    def user_info(self, user):
        bgInfo = self.create_info_widget(f"{user.first_name} {user.surname}", None, None,
                                         user.org, None)
        self.ui.userLayout.addWidget(bgInfo)

    def analyses_info(self, analyses):
        self.ui.analysisTitle.setText(f"{len(analyses)} Analyses")
        self.analysis_number = len(analyses)
        for analysis in analyses:
            bgInfo = self.create_info_widget(analysis.method, analysis.status, analysis.status_date, None,
                                             ANALYSIS_STATUS_COLOUR[analysis.status])
            self.ui.AnalysisLayout.addWidget(bgInfo)
            self.reduction_info(analysis.reduction)

    def reduction_info(self, reduction):
        if reduction:
            self.reductions_number += 1
            bgInfo = self.create_info_widget(reduction.reduction_name, reduction.status, reduction.status_date, None,
                                             REDUCTION_STATUS_COLOUR[reduction.status])
            self.ui.reductionLayout.addWidget(bgInfo)

    def edit_sample(self):
        self.edit_requested.emit("sample", self.sample_id)

    def trigger_card_stated_change(self):
        self.clicked.emit(self)
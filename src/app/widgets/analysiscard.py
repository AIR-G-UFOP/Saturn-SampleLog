from PyQt5 import QtCore, QtGui, QtWidgets
from ..ui.generated.analysiscard import Ui_AnalysisCard
from ..config.settings import (ANALYSIS_CARD_MIN_HEIGHT, TIME_ANIMATION)
from ..utils.utils import get_maximum_height


class AnalysisCard(QtWidgets.QWidget):
    clicked = QtCore.pyqtSignal(object)
    edit_requested = QtCore.pyqtSignal(str, int)

    def __init__(self, analysis):
        super(AnalysisCard, self).__init__()
        self.ui = Ui_AnalysisCard()
        self.ui.setupUi(self)
        self.setMouseTracking(True)
        self.ui.bgCard.setMouseTracking(True)

        self.animation = QtCore.QPropertyAnimation(self.ui.bgCard, b"minimumHeight")
        self.animation.setDuration(TIME_ANIMATION)
        self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)

        self.analysis_id = analysis.id

        self.users_number = 0
        self.reductions_number = 0

        self.ui.analysisTitle.setText(analysis.method)
        self.ui.analysisEquipment.setText(f"Equipment: {analysis.equipment}")
        self.ui.analysisOperator.setText(f"Operator: {analysis.operator}")
        self.ui.analysisConditions.setText(f"Conditions: {analysis.conditions}")
        self.ui.analysisStatus.setText(f"Status: {analysis.status}")
        self.ui.analysisDate.setText(analysis.date.strftime('%Y-%m-%d'))
        self.ui.analysisFile.setText(f"Saved as: {analysis.file_name}")
        self.samples_info(analysis.samples)
        self.reduction_info(analysis.reduction)

        self.ui.userTitle.setText(f"{self.users_number} Users")
        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.ui.panelDLayout.addItem(spacer)
        self.ui.reductionTitle.setText(f"{self.reductions_number} Reductions")
        spacer1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.ui.panelCLayout.addItem(spacer1)

        self.ui.btn_editAnalysis.clicked.connect(self.edit_analysis)

    def mousePressEvent(self, event):
        self.clicked.emit(self)
        super(AnalysisCard, self).mousePressEvent(event)

    def enterEvent(self, event):
        self.ui.bgCard.setStyleSheet(CARD_HOVER_STYLESHEET)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.ui.bgCard.setStyleSheet(CARD_NORMAL_STYLESHEET)
        super().leaveEvent(event)

    def check_card_state(self):
        if self.ui.bgCard.height() == CARD_MIN_HEIGHT:
            self.expand()
        else:
            self.collapse()

    def expand(self):
        self.card_max_height = get_maximum_height(self.ui.horizontalLayout)
        self.animation.setStartValue(CARD_MIN_HEIGHT)
        self.animation.setEndValue(self.card_max_height)
        self.animation.start()

    def collapse(self):
        if self.ui.bgCard.height() != CARD_MIN_HEIGHT:
            self.animation.setStartValue(self.card_max_height)
            self.animation.setEndValue(CARD_MIN_HEIGHT)
            self.animation.start()

    def samples_info(self, samples):
        self.ui.sampleTitle.setText(f"{len(samples)} Samples")
        for sample in samples:
            sname = QtWidgets.QLabel(self)
            sname.setText(sample.name)
            sname.setStyleSheet(CARD_SUBHEADING_TEXT_COLOUR)
            sname.setWordWrap(True)
            sstatus = QtWidgets.QLabel(self)
            sstatus.setText(f"Status: {sample.status}")
            sstatus.setWordWrap(True)
            sdate = QtWidgets.QLabel(self)
            sdate.setText(sample.date.strftime("%d-%m-%Y"))
            sdate.setWordWrap(True)
            self.ui.panelBLayout.addWidget(sname)
            self.ui.panelBLayout.addWidget(sstatus)
            self.ui.panelBLayout.addWidget(sdate)
            self.user_info(sample.users)
        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.ui.panelBLayout.addItem(spacer)

    def user_info(self, user):
        self.users_number += 1
        uname = QtWidgets.QLabel(self)
        uname.setText(f"{user.first_name} {user.surname}")
        uname.setStyleSheet(CARD_SUBHEADING_TEXT_COLOUR)
        uname.setWordWrap(True)
        self.ui.panelDLayout.insertWidget(self.ui.panelDLayout.count() - 1, uname)

    def reduction_info(self, reduction):
        if reduction:
            self.reductions_number += 1
            rname = QtWidgets.QLabel(self)
            rname.setText(reduction.reduction_name)
            rname.setStyleSheet(CARD_SUBHEADING_TEXT_COLOUR)
            rname.setWordWrap(True)
            rstatus = QtWidgets.QLabel(self)
            rstatus.setText(f"Status: {reduction.status}")
            rstatus.setWordWrap(True)
            rdate = QtWidgets.QLabel(self)
            rdate.setText(reduction.date.strftime("%d-%m-%Y"))
            rdate.setWordWrap(True)
            self.ui.panelCLayout.addWidget(rname)
            self.ui.panelCLayout.addWidget(rstatus)
            self.ui.panelCLayout.addWidget(rdate)

    def edit_analysis(self):
        self.edit_requested.emit("analysis", self.analysis_id)
from PyQt5 import QtCore, QtGui, QtWidgets
from ..ui.generated.reductioncard import Ui_ReductionCard
from ..config.settings import (CARD_MIN_HEIGHT, TIME_ANIMATION, CARD_HOVER_STYLESHEET,
                               CARD_NORMAL_STYLESHEET, CARD_SUBHEADING_TEXT_COLOUR)
from ..utils.utils import get_maximum_height


class ReductionCard(QtWidgets.QWidget):
    clicked = QtCore.pyqtSignal(object)
    edit_requested = QtCore.pyqtSignal(str, int)

    def __init__(self, reduction):
        super(ReductionCard, self).__init__()
        self.ui = Ui_ReductionCard()
        self.ui.setupUi(self)
        self.setMouseTracking(True)
        self.ui.bgCard.setMouseTracking(True)

        self.animation = QtCore.QPropertyAnimation(self.ui.bgCard, b"minimumHeight")
        self.animation.setDuration(TIME_ANIMATION)
        self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)

        self.reduction_id = reduction.id

        self.users_number = 0
        self.card_max_height = 200

        self.ui.reductionTitle.setText(reduction.reduction_name)
        self.ui.reductionSoftware.setText(f"Software: {reduction.software}")
        self.ui.reductionSoftwareVersion.setText(f"Software version: {reduction.software_version}")
        self.ui.reductionHandler.setText(f"Handler: {reduction.handler}")
        self.ui.reductionStatus.setText(f"Status: {reduction.status}")
        self.ui.reductionDate.setText(reduction.date.strftime('%Y-%m-%d'))
        self.ui.reductionFile.setText(f"Saved as: {reduction.file_id}")
        self.ui.reductionNotes.setText(f"Notes: {reduction.notes}")
        self.analysis_info(reduction.analysis)

        self.ui.userTitle.setText(f"{self.users_number} Users")
        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.ui.panelDLayout.addItem(spacer)

        self.ui.btn_editReduction.clicked.connect(self.edit_reduction)

    def mousePressEvent(self, event):
        self.clicked.emit(self)
        super(ReductionCard, self).mousePressEvent(event)

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

    def analysis_info(self, analysis):
        self.ui.analysisTitle.setText(analysis.method)
        self.ui.analysisStatus.setText(analysis.status)
        self.ui.analysisDate.setText(analysis.date.strftime('%Y-%m-%d'))
        self.samples_info(analysis.samples)

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
            self.ui.panelCLayout.addWidget(sname)
            self.ui.panelCLayout.addWidget(sstatus)
            self.ui.panelCLayout.addWidget(sdate)
            self.user_info(sample.users)
        spacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.ui.panelCLayout.addItem(spacer)

    def user_info(self, user):
        self.users_number += 1
        uname = QtWidgets.QLabel(self)
        uname.setText(f"{user.first_name} {user.surname}")
        uname.setStyleSheet(CARD_SUBHEADING_TEXT_COLOUR)
        uname.setWordWrap(True)
        self.ui.panelDLayout.insertWidget(self.ui.panelDLayout.count() - 2, uname)

    def edit_reduction(self):
        self.edit_requested.emit("reduction", self.reduction_id)
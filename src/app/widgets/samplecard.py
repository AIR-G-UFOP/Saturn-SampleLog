from PyQt5 import QtCore, QtGui, QtWidgets
from ..ui.generated.samplecard import Ui_SampleCard
from ..config.settings import (CARD_MIN_HEIGHT, TIME_ANIMATION, CARD_HOVER_STYLESHEET,
                               CARD_NORMAL_STYLESHEET, CARD_SUBHEADING_TEXT_COLOUR)
from ..utils.utils import get_maximum_height


class SampleCard(QtWidgets.QWidget):
    clicked = QtCore.pyqtSignal(object)

    def __init__(self, sample):
        super(SampleCard, self).__init__()
        self.ui = Ui_SampleCard()
        self.ui.setupUi(self)
        self.setMouseTracking(True)
        self.ui.bgCard.setMouseTracking(True)

        self.reductions_number = 0
        self.card_max_height = 200

        self.animation = QtCore.QPropertyAnimation(self.ui.bgCard, b"minimumHeight")
        self.animation.setDuration(TIME_ANIMATION)
        self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)

        self.ui.sampleTitle.setText(f"{sample.name}")
        self.ui.sampleDescription.setText(f"{sample.description}")
        self.ui.sampleStatus.setText(f"Status: {sample.status}")
        self.ui.sampleDate.setText(f"{sample.date.strftime('%Y-%m-%d')}")
        self.ui.samplePrep.setText(f"Preparation: {sample.preparation}")
        self.ui.sampleComment.setText(f"Comment: {sample.comment}")
        self.user_info(sample.users)
        self.analyses_info(sample.analyses)


        self.ui.reductionTitle.setText(f"{self.reductions_number} Reductions")
        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.ui.panelDLayout.addItem(spacer)

    def mousePressEvent(self, event):
        self.clicked.emit(self)
        super(SampleCard, self).mousePressEvent(event)

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
        self.card_max_height = self.ui.bgCard.layout().sizeHint().height()
        self.animation.setStartValue(CARD_MIN_HEIGHT)
        self.animation.setEndValue(self.card_max_height)
        self.animation.start()

    def expand(self):
        self.card_max_height = get_maximum_height(self.ui.horizontalLayout)
        self.animation.setStartValue(CARD_MIN_HEIGHT)
        self.animation.setEndValue(self.card_max_height)
        self.animation.start()

    def user_info(self, user):
        self.ui.userTitle.setText(f"{user.first_name} {user.surname}")
        self.ui.userOrg.setText(f"{user.org}")
        self.ui.userAddress.setText(f"{user.address}")
        self.ui.userPhone.setText(f"{user.phone}")
        self.ui.userEmail.setText(f"{user.email}")

    def analyses_info(self, analyses):
        self.ui.analysisTitle.setText(f"{len(analyses)} Analyses")
        for analysis in analyses:
            aname = QtWidgets.QLabel(self)
            aname.setText(analysis.method)
            aname.setStyleSheet(CARD_SUBHEADING_TEXT_COLOUR)
            aname.setWordWrap(True)
            astatus = QtWidgets.QLabel(self)
            astatus.setText(f"Status: {analysis.status}")
            astatus.setWordWrap(True)
            adate = QtWidgets.QLabel(self)
            adate.setText(analysis.date.strftime("%d-%m-%Y"))
            adate.setWordWrap(True)
            self.ui.panelCLayout.addWidget(aname)
            self.ui.panelCLayout.addWidget(astatus)
            self.ui.panelCLayout.addWidget(adate)
            self.reduction_info(analysis.reduction)
        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.ui.panelCLayout.addItem(spacer)

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
            self.ui.panelDLayout.addWidget(rname)
            self.ui.panelDLayout.addWidget(rstatus)
            self.ui.panelDLayout.addWidget(rdate)
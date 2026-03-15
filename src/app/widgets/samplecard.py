from PyQt5 import QtCore, QtGui, QtWidgets
from ..ui.generated.samplecard import Ui_SampleCard
from ..config.settings import (CARD_MAX_HEIGHT, CARD_MIN_HEIGHT, TIME_ANIMATION, CARD_HOVER_STYLESHEET,
                               CARD_NORMAL_STYLESHEET, CARD_SUBHEADING_TEXT_COLOUR)

class SampleCard(QtWidgets.QWidget):
    clicked = QtCore.pyqtSignal(object)

    def __init__(self, sample):
        super(SampleCard, self).__init__()
        self.ui = Ui_SampleCard()
        self.ui.setupUi(self)
        self.setMouseTracking(True)
        self.ui.bgCard.setMouseTracking(True)

        self.analyses_number = 0
        self.reductions_number = 0

        self.ui.sampleTitle.setText(f"{sample.name}")
        self.ui.sampleDescription.setText(f"{sample.description}")
        self.ui.sampleStatus.setText(f"Status: {sample.status}")
        self.ui.sampleDate.setText(f"{sample.date.strftime('%Y-%m-%d')}")
        self.ui.samplePrep.setText(f"Preparation: {sample.preparation}")
        self.ui.sampleComment.setText(f"Comment: {sample.comment}")
        self.user_info(sample.users)
        self.analyses_info(sample.analyses)

        self.ui.analysisTitle.setText(f"{self.analyses_number} analyses")
        self.ui.reductionTitle.setText(f"{self.reductions_number} reductions")
        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.ui.panelBLayout.addItem(spacer)
        spacer1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.ui.panelCLayout.addItem(spacer1)
        spacer2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.ui.panelDLayout.addItem(spacer2)

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
        self.animation = QtCore.QPropertyAnimation(self.ui.bgCard, b"minimumHeight")
        self.animation.setDuration(TIME_ANIMATION)
        self.animation.setStartValue(CARD_MIN_HEIGHT)
        self.animation.setEndValue(CARD_MAX_HEIGHT)
        self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.animation.start()

    def collapse(self):
        self.animation = QtCore.QPropertyAnimation(self.ui.bgCard, b"minimumHeight")
        self.animation.setDuration(TIME_ANIMATION)
        self.animation.setStartValue(CARD_MAX_HEIGHT)
        self.animation.setEndValue(CARD_MIN_HEIGHT)
        self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.animation.start()

    def user_info(self, user):
        self.ui.userTitle.setText(f"{user.first_name} {user.surname}")
        self.ui.userOrg.setText(f"{user.org}")
        self.ui.userAddress.setText(f"{user.address}")
        self.ui.userPhone.setText(f"{user.phone}")
        self.ui.userEmail.setText(f"{user.email}")

    def analyses_info(self, analyses):
        self.analyses_number += len(analyses)
        for analysis in analyses:
            aname = QtWidgets.QLabel(self)
            aname.setText(analysis.method)
            aname.setStyleSheet(CARD_SUBHEADING_TEXT_COLOUR)
            astatus = QtWidgets.QLabel(self)
            astatus.setText(f"Status: {analysis.status}")
            adate = QtWidgets.QLabel(self)
            adate.setText(analysis.date.strftime("%d-%m-%Y"))
            self.ui.panelCLayout.addWidget(aname)
            self.ui.panelCLayout.addWidget(astatus)
            self.ui.panelCLayout.addWidget(adate)
            self.reduction_info(analysis.reduction)

    def reduction_info(self, reduction):
        if reduction:
            self.reductions_number += 1
            rname = QtWidgets.QLabel(self)
            rname.setText(reduction.reduction_name)
            rname.setStyleSheet(CARD_SUBHEADING_TEXT_COLOUR)
            rstatus = QtWidgets.QLabel(self)
            rstatus.setText(f"Status: {reduction.status}")
            rdate = QtWidgets.QLabel(self)
            rdate.setText(reduction.date.strftime("%d-%m-%Y"))
            self.ui.panelDLayout.addWidget(rname)
            self.ui.panelDLayout.addWidget(rstatus)
            self.ui.panelDLayout.addWidget(rdate)
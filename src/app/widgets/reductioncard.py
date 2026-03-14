from PyQt5 import QtCore, QtGui, QtWidgets
from ..ui.generated.reductioncard import Ui_ReductionCard

class ReductionCard(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ReductionCard, self).__init__(parent)
        self.ui = Ui_ReductionCard()
        self.ui.setupUi(self)
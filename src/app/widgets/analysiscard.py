from PyQt5 import QtCore, QtGui, QtWidgets
from ..ui.generated.analysiscard import Ui_AnalysisCard

class AnalysisCard(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(AnalysisCard, self).__init__(parent)
        self.ui = Ui_AnalysisCard()
        self.ui.setupUi(self)
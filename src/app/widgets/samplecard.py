from PyQt5 import QtCore, QtGui, QtWidgets
from ..ui.generated.samplecard import Ui_SampleCard

class SampleCard(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(SampleCard, self).__init__(parent)
        self.ui = Ui_SampleCard()
        self.ui.setupUi(self)
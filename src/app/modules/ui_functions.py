from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QSizeGrip
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtCore import QEvent, QTimer, Qt
from ..widgets.custom_grips import CustomGrip
from ..config.settings import ENABLE_CUSTOM_TITLE_BAR


GLOBAL_STATE = False
GLOBAL_TITLE_BAR = True


class UIFunctions():
    def maximize_restore(self):
        global GLOBAL_STATE
        status = GLOBAL_STATE
        if status == False:
            self.showMaximized()
            GLOBAL_STATE = True
            self.ui.shadow.setContentsMargins(0, 0, 0, 0)
            self.ui.maximizeRestoreAppBtn.setToolTip("Restore")
            self.ui.maximizeRestoreAppBtn.setIcon(QIcon(u":/icons/icons/icon_restore.png"))
            self.ui.frame_size_grip.hide()
            self.left_grip.hide()
            self.right_grip.hide()
            self.top_grip.hide()
            self.bottom_grip.hide()
        else:
            GLOBAL_STATE = False
            self.showNormal()
            self.resize(self.width() + 1, self.height() + 1)
            self.ui.shadow.setContentsMargins(10, 10, 10, 10)
            try:
                self.ui.maximizeRestoreAppBtn.setToolTip("Maximize")
                self.ui.maximizeRestoreAppBtn.setIcon(QIcon(u":/icons/icons/icon_maximize.png"))
            except:
                pass

            self.ui.frame_size_grip.show()
            self.left_grip.show()
            self.right_grip.show()
            self.top_grip.show()
            self.bottom_grip.show()

    def returStatus(self):
        return GLOBAL_STATE

    def setStatus(self, status):
        global GLOBAL_STATE
        GLOBAL_STATE = status

    def uiDefinitions(self):
        def dobleClickMaximizeRestore(event):
            # IF DOUBLE CLICK CHANGE STATUS
            if event.type() == QEvent.MouseButtonDblClick:
                QTimer.singleShot(250, lambda: UIFunctions.maximize_restore(self))

        self.ui.titleGripFrame.mouseDoubleClickEvent = dobleClickMaximizeRestore

        if ENABLE_CUSTOM_TITLE_BAR:
            # STANDARD TITLE BAR
            self.setWindowFlags(Qt.FramelessWindowHint)
            self.setAttribute(Qt.WA_TranslucentBackground)

            # MOVE WINDOW / MAXIMIZE / RESTORE
            def moveWindow(event):
                # IF MAXIMIZED CHANGE TO NORMAL
                if UIFunctions.returStatus(self):
                    UIFunctions.maximize_restore(self)
                # MOVE WINDOW
                if event.buttons() == Qt.LeftButton:
                    self.move(self.pos() + event.globalPos() - self.dragPos)
                    self.dragPos = event.globalPos()
                    event.accept()

            self.ui.titleGripFrame.mouseMoveEvent = moveWindow

            self.left_grip = CustomGrip(self, Qt.LeftEdge, True)
            self.right_grip = CustomGrip(self, Qt.RightEdge, True)
            self.top_grip = CustomGrip(self, Qt.TopEdge, True)
            self.bottom_grip = CustomGrip(self, Qt.BottomEdge, True)

        else:
            self.ui.appMargins.setContentsMargins(0, 0, 0, 0)
            self.ui.minimizeAppBtn.hide()
            self.ui.maximizeRestoreAppBtn.hide()
            self.ui.closeAppBtn.hide()
            self.ui.frame_size_grip.hide()

        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(17)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 150))
        self.ui.bgApp.setGraphicsEffect(self.shadow)

        try:
            self.sizegrip = QSizeGrip(self.ui.frame_size_grip)
            self.sizegrip.setStyleSheet("width: 20px; height: 20px; margin 0px; padding: 0px;")
        except:
            pass

        try:
            self.ui.minimizeAppBtn.clicked.connect(lambda: self.showMinimized())
        except:
            pass

        try:
            self.ui.maximizeRestoreAppBtn.clicked.connect(lambda: UIFunctions.maximize_restore(self))
        except:
            pass

    def resize_grips(self):
        if ENABLE_CUSTOM_TITLE_BAR:
            self.left_grip.setGeometry(0, 10, 10, self.height())
            self.right_grip.setGeometry(self.width() - 10, 10, 10, self.height())
            self.top_grip.setGeometry(0, 0, self.width(), 10)
            self.bottom_grip.setGeometry(0, self.height() - 10, self.width(), 10)

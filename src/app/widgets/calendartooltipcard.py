from PyQt5.QtWidgets import (QLabel, QVBoxLayout, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen


class TooltipCard(QFrame):
    def __init__(self, title, details, date_text, parent=None):
        super().__init__(parent, Qt.ToolTip)
        self.setObjectName("tooltipCard")
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)

        self.setStyleSheet("""
            QLabel {
                color: #d6dcff;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        title_lbl = QLabel(f"• {title}")
        title_lbl.setStyleSheet("font-weight: bold; color:#aee3ff;")

        details_lbl = QLabel(details)
        details_lbl.setWordWrap(True)

        date_lbl = QLabel(date_text)
        date_lbl.setStyleSheet("color:#9aa3c7; font-size:10px;")

        layout.addWidget(title_lbl)
        layout.addWidget(details_lbl)
        layout.addWidget(date_lbl)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(0, 0, -1, -1)
        bg_color = QColor("#2b2f3f")
        border_color = QColor("#3a3f5a")
        painter.setBrush(QBrush(bg_color))
        pen = QPen(border_color)
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawRoundedRect(rect, 10, 10)
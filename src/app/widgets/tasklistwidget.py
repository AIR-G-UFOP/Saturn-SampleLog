from typing import Optional, List

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
)
from .calendarwidget import (CalendarTask,
                             format_date_range,
                             COLOURS,
                             CATEGORY_COLORS)


def sort_tasks(tasks: List[CalendarTask]) -> List[CalendarTask]:
    return sorted(tasks, key=lambda item: (item.start, item.end, item.title.lower()))


class TaskListItem(QFrame):
    navigate_requested = pyqtSignal(int)
    edit_requested = pyqtSignal(int)
    delete_requested = pyqtSignal(int)

    def __init__(self, task: CalendarTask, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.task_data = task
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(
            "QFrame {"
            f"background: {COLOURS['bg1']};"
            f"border: 1px solid {COLOURS['border']};"
            "border-radius: 14px;"
            "}"
        )
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(2)

        accent = QFrame()
        accent.setFixedWidth(5)
        accent.setStyleSheet(
            f"background: {CATEGORY_COLORS[self.task_data.category]}; border: none; border-radius: 2px;"
        )
        layout.addWidget(accent)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(10, 0, 0, 0)
        content_layout.setSpacing(2)

        title = QLabel(self.task_data.title)
        title.setFont(QFont("Inter", 9, QFont.Bold))
        title.setStyleSheet(f"color: {COLOURS['fg']}; border: none;")

        meta = QLabel(
            f"{self.task_data.category} • {format_date_range(self.task_data)}"
        )
        meta.setFont(QFont("Inter", 8, QFont.Bold))
        meta.setStyleSheet(f"color: {COLOURS['muted']}; border: none;")

        description = QLabel(self.task_data.description)
        description.setFont(QFont("Inter", 8, QFont.Bold))
        description.setWordWrap(True)
        description.setStyleSheet(f"color: {COLOURS['comment']}; border: none;")

        content_layout.addWidget(title)
        content_layout.addWidget(meta)
        content_layout.addWidget(description)
        layout.addLayout(content_layout, 1)

        actions_layout = QVBoxLayout()
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(2)

        self.edit_button = self._make_action_button("")
        self.delete_button = self._make_action_button("", destructive=True)
        self.edit_button.setIcon(QIcon(":icons/icons/cil-edit-calendar.png"))
        self.delete_button.setIcon(QIcon(":icons/icons/cil-remove-task.png"))

        self.edit_button.clicked.connect(lambda: self.edit_requested.emit(self.task_data.task_id))
        self.delete_button.clicked.connect(lambda: self.delete_requested.emit(self.task_data.task_id))

        actions_layout.addWidget(self.edit_button)
        actions_layout.addWidget(self.delete_button)
        actions_layout.addStretch(1)
        layout.addLayout(actions_layout)

    def _make_action_button(self, text: str, destructive: bool = False) -> QPushButton:
        button = QPushButton(text)
        button.setCursor(Qt.PointingHandCursor)
        button.setMinimumHeight(25)
        button.setMaximumHeight(25)
        button.setMinimumWidth(25)
        button.setMaximumWidth(25)
        button.setStyleSheet(
            "QPushButton {"
            f"background: {'rgba(255,85,85,0.16)' if destructive else COLOURS['bg2']};"
            f"border: 1px solid {COLOURS['red'] if destructive else COLOURS['border']};"
            f"color: {COLOURS['red'] if destructive else COLOURS['fg']};"
            "border-radius: 8px;"
            "padding: 4px 12px;"
            "font-size: 10px;"
            "font-weight: 600;"
            "}"
            "QPushButton:hover {"
            f"background: {'rgba(255,85,85,0.24)' if destructive else COLOURS['bg3']};"
            "}"
        )
        return button

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.navigate_requested.emit(self.task_data.task_id)
        super().mousePressEvent(event)



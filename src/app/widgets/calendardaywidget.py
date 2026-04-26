from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QFrame, QSizePolicy, QHBoxLayout, QScrollArea, QApplication)
from PyQt5.QtCore import (
    Qt, QDate, pyqtSignal, QPoint)
from .calendartooltipcard import TooltipCard



class DayWidget(QFrame):
    clicked = pyqtSignal(QDate, bool)
    doubleClicked = pyqtSignal(QDate)
    taskClicked = pyqtSignal(object)

    def __init__(self, date, is_current_month=True, is_today=False, tasks=None, style=None, parent=None):
        super().__init__(parent)
        self.date = date
        self.tasks = tasks or []
        self.is_current_month = is_current_month
        self.is_today = is_today
        self.style = style or {}

        self.tooltip = None

        self.setObjectName("dayWidget")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setCursor(Qt.PointingHandCursor)

        self.base_style = ""
        self.apply_style()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        header = QHBoxLayout()

        self.date_label = QLabel(str(date.day()))
        base_date_style = self.style.get("date_label", "color: #d6dcff; font-weight: bold;")
        if not self.is_current_month:
            base_date_style += self.style.get("faded_text", "color: #44475A;")
        self.date_label.setStyleSheet(base_date_style)

        header.addWidget(self.date_label, alignment=Qt.AlignLeft)

        if self.is_today:
            badge = QLabel("Today")
            badge.setStyleSheet(self.style.get("today_badge", "background:#5c6bc0;color:white;border-radius:6px;padding:2px 4px;font-size:9px;"))
            header.addWidget(badge, alignment=Qt.AlignRight)

        layout.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        container = QWidget()
        v = QVBoxLayout(container)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(2)

        for task in self.tasks:
            label = QLabel(task.name)
            label.setWordWrap(True)

            label.enterEvent = lambda e, tsk=task, lbl=label: self.show_tooltip(tsk, lbl)
            label.leaveEvent = lambda e: self.hide_tooltip()
            label.mousePressEvent = lambda e, tsk=task: self.edit_task(tsk)

            task_style = self.style.get(task.task_type,
                                        "background:#6272A4;color:#F8F8F2;border-radius:6px;padding:2px 4px;font-size:8px;")
            if not self.is_current_month:
                task_style += self.style.get("faded_text", "color:#6b6f8a;")
            label.setStyleSheet(task_style)
            v.addWidget(label)

        v.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)

    def show_tooltip(self, task, widget):
        self.hide_tooltip()

        self.tooltip = TooltipCard(
            title=task.name,
            details=task.description,
            date_text=self.date.toString()
        )

        self.tooltip.adjustSize()

        # Base position (stable anchor: above cell with smart horizontal flipping)
        anchor_pos = widget.mapToGlobal(QPoint(0, 0))

        # Default: align left
        x = anchor_pos.x()
        y = anchor_pos.y() - self.tooltip.height() - 8

        # Screen geometry
        screen_obj = QApplication.screenAt(anchor_pos)
        if not screen_obj:
            screen_obj = QApplication.primaryScreen()
        screen = screen_obj.availableGeometry()

        # Flip to right-align if overflowing right
        if x + self.tooltip.width() > screen.right():
            x = anchor_pos.x() + widget.width() - self.tooltip.width()

        # Clamp if still out of bounds
        if x < screen.left():
            x = screen.left() + 8

        # Screen geometry
        # Detect correct screen (multi-monitor aware)
        screen_obj = QApplication.screenAt(anchor_pos)
        if not screen_obj:
            screen_obj = QApplication.primaryScreen()
        screen = screen_obj.availableGeometry()

        # Adjust horizontally if overflowing right
        if x + self.tooltip.width() > screen.right():
            x = screen.right() - self.tooltip.width() - 10

        # Adjust vertically if overflowing bottom
        if y + self.tooltip.height() > screen.bottom():
            y = anchor_pos.y() - self.tooltip.height() - 10

        # Prevent going off left/top
        if x < screen.left():
            x = screen.left() + 10
        if y < screen.top():
            y = screen.top() + 10

        self.tooltip.move(x, y)
        self.tooltip.show()

    def hide_tooltip(self):
        if self.tooltip:
            self.tooltip.close()
            self.tooltip = None

    def apply_style(self):
        base = self.style.get("day", "border:1px solid #343746;border-radius:10px;background:#343746;")

        if not self.is_current_month:
            base += self.style.get("other_month", "background:#282A36;border:1px solid #282A36;")

        if self.is_today:
            base += self.style.get("today", "border:1px solid #5c6bc0;")

        self.base_style = base
        self.setStyleSheet(f"QFrame#dayWidget {{{base}}}")

    def enterEvent(self, event):
        hover = self.style.get("hover", "background:#1b2040;")
        self.setStyleSheet(f"QFrame#dayWidget {{{self.base_style + hover}}}")

    def leaveEvent(self, event):
        self.setStyleSheet(f"QFrame#dayWidget {{{self.base_style}}}")

    def mousePressEvent(self, event):
        self.clicked.emit(self.date, self.is_current_month)

    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit(self.date)

    def edit_task(self, task):
        self.taskClicked.emit(task)
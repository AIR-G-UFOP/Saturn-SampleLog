import sys
from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QLabel, QVBoxLayout, QFrame, QSizePolicy, QHBoxLayout, QScrollArea, QApplication)
from PyQt5.QtCore import (
    Qt, QDate, pyqtSignal, QPoint)


class TooltipCard(QFrame):
    def __init__(self, title, details, date_text, parent=None):
        super().__init__(parent, Qt.ToolTip)
        self.setObjectName("tooltipCard")
        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)

        self.setStyleSheet("""
            QFrame#tooltipCard {
                background: #2b2f3f;
                border: 1px solid #3a3f5a;
                border-radius: 10px;
            }
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


class DayWidget(QFrame):
    clicked = pyqtSignal(QDate, bool)
    doubleClicked = pyqtSignal(QDate)
    taskClicked = pyqtSignal()

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
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

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
            label = QLabel(task)
            label.setWordWrap(True)

            label.enterEvent = lambda e, tsk=task, lbl=label: self.show_tooltip(tsk, lbl)
            label.leaveEvent = lambda e: self.hide_tooltip()
            label.mousePressEvent = lambda e, tsk=task: self.edit_task(tsk)

            task_style = self.style.get("task", "background:#3b4266;color:white;border-radius:6px;padding:2px 4px;font-size:10px;")
            if not self.is_current_month:
                task_style += self.style.get("faded_text", "color:#6b6f8a;")
            label.setStyleSheet(task_style)
            v.addWidget(label)

        v.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)

    def show_tooltip(self, task_text, widget):
        self.hide_tooltip()

        self.tooltip = TooltipCard(
            title=task_text,
            details="Detailed description here...",
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

    def edit_task(self, task_text):
        self.taskClicked.emit()


class CalendarWidget(QWidget):
    dateClicked = pyqtSignal(QDate)
    monthChanged = pyqtSignal(int, int)
    calendarRefresh = pyqtSignal(int, int)
    createTask = pyqtSignal()
    editTask = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.current_date = QDate.currentDate()
        self.tasks = {}
        self.style = {}

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(2)

        self.build_day_names()
        self.build_calendar()

    def build_day_names(self):
        days_layout = QGridLayout()
        days_layout.setSpacing(2)

        for col, name in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
            label = QLabel(name)
            label.setAlignment(Qt.AlignCenter)
            days_layout.addWidget(label, 0, col)

        self.main_layout.addLayout(days_layout)

    def build_calendar(self):
        self.grid = QGridLayout()
        self.grid.setSpacing(2)
        self.main_layout.addLayout(self.grid)
        self.refresh()

    def refresh(self):
        while self.grid.count():
            child = self.grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        year = self.current_date.year()
        month = self.current_date.month()
        self.calendarRefresh.emit(year, month)

        first_day = QDate(year, month, 1)
        start_day = first_day.dayOfWeek()
        days_in_month = first_day.daysInMonth()

        prev_month = first_day.addMonths(-1)
        prev_days = prev_month.daysInMonth()

        row, col = 0, 0

        for i in range(start_day - 1):
            day = prev_days - (start_day - 2 - i)
            date = QDate(prev_month.year(), prev_month.month(), day)
            self.add_day_widget(date, row, col, False)
            col += 1

        for day in range(1, days_in_month + 1):
            date = QDate(year, month, day)
            if col > 6:
                col = 0
                row += 1
            self.add_day_widget(date, row, col, True)
            col += 1

        next_day = 1
        while col <= 6:
            date = QDate(year, month, days_in_month).addDays(next_day)
            self.add_day_widget(date, row, col, False)
            col += 1
            next_day += 1

    def add_day_widget(self, date, row, col, is_current_month):
        is_today = date == QDate.currentDate()
        tasks = self.tasks.get(date, [])

        widget = DayWidget(date, is_current_month, is_today, tasks, self.style)
        widget.clicked.connect(self.handle_day_click)
        widget.doubleClicked.connect(self.create_task)
        widget.taskClicked.connect(self.edit_task)

        self.grid.addWidget(widget, row, col)

    def on_month_changed(self, index):
        self.set_month(self.current_date.year(), index + 1)

    def on_year_changed(self, text):
        self.set_month(int(text), self.current_date.month())

    def set_month(self, year, month):
        self.current_date = QDate(year, month, 1)
        self.refresh()

    def prev_month(self):
        self.current_date = self.current_date.addMonths(-1)
        self.refresh()

    def next_month(self):
        self.current_date = self.current_date.addMonths(1)
        self.refresh()

    def handle_day_click(self, date, is_current_month):
        if not is_current_month:
            self.set_month(date.year(), date.month())
        self.dateClicked.emit(date)

    def edit_task(self):
        self.editTask.emit()

    def create_task(self, date):
        # dialog = EventDialog(date, parent=self)
        # if dialog.exec_():
        #     text = dialog.title.text()
        #     if text:
        #         self.add_task(date, text)
        self.createTask.emit()

    def update_tasks(self):
        # self.tasks.setdefault(date, []).append(text)
        # self.refresh()
        pass

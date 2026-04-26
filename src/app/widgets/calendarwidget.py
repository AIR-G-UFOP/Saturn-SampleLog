import sys
from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QLabel, QVBoxLayout, QFrame, QSizePolicy, QHBoxLayout, QScrollArea, QApplication)
from PyQt5.QtCore import (
    Qt, QDate, pyqtSignal, pyqtSlot)
from .calendardaywidget import DayWidget


class CalendarWidget(QWidget):
    dateClicked = pyqtSignal(QDate)
    monthChanged = pyqtSignal(int, int)
    calendarRefresh = pyqtSignal(int, int)
    createTask = pyqtSignal(QDate)
    editTask = pyqtSignal(object)

    def __init__(self, task_service):
        super().__init__()

        self.current_date = QDate.currentDate()
        self.taskService = task_service
        self.style = {
            "sample_preparation": "background:#BD93F9;color:#282A36;border-radius:6px;padding:2px 4px;font-size:9px;",
            "analysis": "background:#F1FA8C;color:#282A36;border-radius:6px;padding:2px 4px;font-size:9px;",
            "reduction": "background:#FFB86C;color:#282A36;border-radius:6px;padding:2px 4px;font-size:9px;",
        }

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
        for i in range(7):
            self.grid.setColumnStretch(i, 1)
        for i in range(6):
            self.grid.setRowStretch(i, 1)
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
        tasks = self.taskService.getTasksByDate(date.toPyDate())

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

    @pyqtSlot(object)
    def edit_task(self, task):
        self.editTask.emit(task)

    @pyqtSlot(QDate)
    def create_task(self, date):
        self.createTask.emit(date)

import PyQt5

from ..widgets.calendarwidget import CalendarWidget
from PyQt5.QtCore import QDate, pyqtSlot

class Timetable:
    def __init__(self, ui):
        self.ui = ui
        self.calendar = CalendarWidget()
        self.ui.calendarLayout.addWidget(self.calendar)
        self.setup_header()
        self.calendar.createTask.connect(self.create_task)
        self.calendar.editTask.connect(self.edit_task)

    def setup_header(self):
        self.ui.comboMonth.addItems([QDate.longMonthName(i) for i in range(1, 13)])
        self.ui.comboYear.addItems([str(y) for y in range(1970, 2101)])
        self.ui.comboMonth.setCurrentIndex(QDate.currentDate().month() - 1)
        self.ui.comboYear.setCurrentText(str(QDate.currentDate().year()))
        self.ui.btn_previousMonth.clicked.connect(
            lambda: self.calendar.prev_month())
        self.ui.btn_nextMonth.clicked.connect(
            lambda: self.calendar.next_month())
        self.ui.comboMonth.currentIndexChanged.connect(
            lambda: self.calendar.on_month_changed(self.ui.comboMonth.currentIndex()))
        self.ui.comboYear.currentIndexChanged.connect(
            lambda: self.calendar.on_year_changed(self.ui.comboYear.currentText()))
        self.calendar.calendarRefresh.connect(self.refresh_header)

    def refresh_header(self, year, month):
        self.ui.comboMonth.setCurrentIndex(month - 1)
        self.ui.comboYear.setCurrentText(str(year))

    def edit_task(self):
        print("edit_task")

    def create_task(self):
        print("add_task")

    def add_task(self):
        pass
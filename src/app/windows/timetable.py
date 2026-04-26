from PyQt5 import QtCore

from ..widgets.calendarwidget import CalendarWidget
from PyQt5.QtCore import QDate, pyqtSignal


class Timetable(QtCore.QObject):
    addTask = pyqtSignal(QDate)
    
    def __init__(self, calendarLayout, comboMonth, comboYear, previousMonth, nextMonth, btn_addtask, task_service,
                 parent=None):
        super(Timetable, self).__init__(parent)

        self.calendar = CalendarWidget(task_service)
        calendarLayout.addWidget(self.calendar)
        self.comboMonth = comboMonth
        self.comboYear = comboYear
        self.previousMonth = previousMonth
        self.nextMonth = nextMonth

        self.setup_header()
        self.calendar.createTask.connect(self.create_task)
        self.calendar.editTask.connect(self.edit_task)
        btn_addtask.clicked.connect(self.create_task)

    def setup_header(self):
        self.comboMonth.addItems([QDate.longMonthName(i) for i in range(1, 13)])
        self.comboYear.addItems([str(y) for y in range(1970, 2101)])
        self.comboMonth.setCurrentIndex(QDate.currentDate().month() - 1)
        self.comboYear.setCurrentText(str(QDate.currentDate().year()))
        self.previousMonth.clicked.connect(
            lambda: self.calendar.prev_month())
        self.nextMonth.clicked.connect(
            lambda: self.calendar.next_month())
        self.comboMonth.currentIndexChanged.connect(
            lambda: self.calendar.on_month_changed(self.comboMonth.currentIndex()))
        self.comboYear.currentIndexChanged.connect(
            lambda: self.calendar.on_year_changed(self.comboYear.currentText()))
        self.calendar.calendarRefresh.connect(self.refresh_header)

    def refresh_header(self, year, month):
        self.comboMonth.setCurrentIndex(month - 1)
        self.comboYear.setCurrentText(str(year))

    def edit_task(self):
        pass

    def create_task(self, date):
        if not date:
            date = QDate.currentDate()
        self.addTask.emit(date)

    def refresh(self):
        self.calendar.refresh()
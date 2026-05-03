from PyQt5 import QtCore
from PyQt5.QtCore import QDate, pyqtSignal
from datetime import date
from typing import List

from PyQt5.QtWidgets import QLabel

from ..widgets.calendarwidget import (
    CalendarMonthView,
    first_of_month,
    CalendarTask,
)
from ..widgets.tasklistwidget import TaskListItem, sort_tasks


class Timetable(QtCore.QObject):
    addTask = pyqtSignal(object)
    editTask = pyqtSignal(object)
    deleteTask = pyqtSignal(object)
    
    def __init__(self, calendarLayout, comboMonth, comboYear, previousMonth, nextMonth, btn_today, btn_addtask,
                 task_service, taskListLayout, taskCountLabel,
                 parent=None):
        super(Timetable, self).__init__(parent)

        self.taskService = task_service
        self.current_month = first_of_month(date.today())
        self.task_cards: List[TaskListItem] = []

        self.comboMonth = comboMonth
        self.comboYear = comboYear
        self.previousMonth = previousMonth
        self.nextMonth = nextMonth
        self.btn_today = btn_today
        self.taskListLayout = taskListLayout
        self.taskCountLabel = taskCountLabel
        self.setup_controls()

        self.calendar = CalendarMonthView(task_service)
        self.calendar.add_requested.connect(self.create_task)
        self.calendar.edit_requested.connect(self.edit_task)
        calendarLayout.addWidget(self.calendar)
        btn_addtask.clicked.connect(self.create_task)

        self.tasks = self.get_tasks()
        self.refresh_calendar()

    def setup_controls(self):
        self.comboMonth.addItems([QDate.longMonthName(i) for i in range(1, 13)])
        self.comboYear.addItems([str(y) for y in range(1970, 2101)])
        self.comboMonth.setCurrentIndex(QDate.currentDate().month() - 1)
        self.comboYear.setCurrentText(str(QDate.currentDate().year()))
        self.previousMonth.clicked.connect(self.handle_previous_next_click)
        self.nextMonth.clicked.connect(self.handle_previous_next_click)
        self.comboMonth.currentIndexChanged.connect(self.handle_month_year_change)
        self.comboYear.currentIndexChanged.connect(self.handle_month_year_change)
        self.btn_today.clicked.connect(self.jump_to_today)
        self.sync_controls_to_current_month()

    def get_tasks(self):
        tasks = self.taskService.getTasksByMonth(self.current_month.month, self.current_month.year)
        return [
            CalendarTask(
                task.id,
                task.name,
                task.description,
                task.start_date,
                task.end_date,
                task.task_type)
            for task in tasks]

    def handle_previous_next_click(self):
        sender = self.sender()
        current_month = self.comboMonth.currentIndex()
        if sender == self.previousMonth and current_month != 0:
            self.comboMonth.setCurrentIndex(current_month - 1)
        elif sender == self.nextMonth and current_month != 11:
            self.comboMonth.setCurrentIndex(current_month + 1)

    def handle_month_year_change(self):
        month = self.comboMonth.currentIndex() + 1
        year = int(self.comboYear.currentText())
        self.current_month = date(year, month, 1)
        self.tasks = self.get_tasks()
        self.refresh_calendar()

    def jump_to_today(self):
        self.current_month = first_of_month(date.today())
        self.tasks = self.get_tasks()
        self.refresh_calendar()

    def sync_controls_to_current_month(self):
        self.comboMonth.blockSignals(True)
        self.comboYear.blockSignals(True)
        self.comboMonth.setCurrentIndex(self.current_month.month - 1)
        self.comboYear.setCurrentText(str(self.current_month.year))
        self.comboMonth.blockSignals(False)
        self.comboYear.blockSignals(False)

    def handle_task_focus_request(self, task_id: int):
        task = self.find_task(task_id)
        if task is None:
            return
        self.current_month = first_of_month(task.start_date)
        self.refresh_calendar()

    def refresh_calendar(self):
        self.sync_controls_to_current_month()
        self.tasks = self.get_tasks()
        self.calendar.set_month_and_tasks(self.current_month, self.tasks)
        self.refresh_task_list()

    def refresh_task_list(self):
        while self.taskListLayout.count():
            item = self.taskListLayout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        self.task_cards = []
        tasks = self.taskService.getAllTasks()
        sorted_tasks = sort_tasks([
            CalendarTask(
                task.id,
                task.name,
                task.description,
                task.start_date,
                task.end_date,
                task.task_type)
            for task in tasks])
        if not sorted_tasks:
            self.taskCountLabel.setText("0 Tasks")
            empty_label = QLabel("No tasks loaded")
            empty_label.setStyleSheet("color: #BFBFBF; font-size: 11px;")
            self.taskListLayout.addWidget(empty_label)
            self.taskListLayout.addStretch(1)
            return
        for task in sorted_tasks:
            card = TaskListItem(task)
            card.navigate_requested.connect(self.handle_task_focus_request)
            card.edit_requested.connect(self.edit_task)
            card.delete_requested.connect(self.delete_task)
            self.taskListLayout.addWidget(card)
            self.task_cards.append(card)
        self.taskCountLabel.setText(f"{len(sorted_tasks)} Tasks")
        self.taskListLayout.addStretch(1)

    def find_task(self, task_id_to_find: int):
        return self.taskService.getTaskById(task_id_to_find)

    def edit_task(self, task_id_to_edit: int):
        task = self.find_task(task_id_to_edit)
        self.editTask.emit(task)

    def create_task(self, clicked_date: date):
        if not clicked_date:
            clicked_date = date.today()
        self.addTask.emit(clicked_date)

    def delete_task(self, task_id_to_delete: int):
        task = self.find_task(task_id_to_delete)
        self.deleteTask.emit(task)


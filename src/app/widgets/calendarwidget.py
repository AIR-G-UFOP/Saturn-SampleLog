from dataclasses import dataclass
from datetime import date, timedelta
from typing import Dict, List, Optional

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

COLOURS: Dict[str, str] = {
    "bg0": "#191A21",
    "bg1": "#21222C",
    "bg2": "#282A36",
    "bg3": "#343746",
    "border": "#44475A",
    "fg": "#F8F8F2",
    "muted": "#BFBFBF",
    "comment": "#6272A4",
    "cyan": "#8BE9FD",
    "green": "#50FA7B",
    "orange": "#FFB86C",
    "pink": "#FF79C6",
    "purple": "#BD93F9",
    "red": "#FF5555",
    "yellow": "#F1FA8C",
}

CATEGORY_STYLES = {
    "sample_preparation": {"color": COLOURS["purple"], "bg": "rgba(189,147,249,0.18)"},
    "other": {"color": COLOURS["cyan"], "bg": "rgba(139,233,253,0.18)"},
    "reduction": {"color": COLOURS["orange"], "bg": "rgba(255,184,108,0.18)"},
    "analysis": {"color": COLOURS["yellow"], "bg": "rgba(241, 250, 140, 0.18)"},
}

CATEGORY_COLORS = {"sample_preparation": COLOURS["purple"],
                   "other": COLOURS["cyan"],
                   "reduction": COLOURS["orange"],
                   "analysis": COLOURS["yellow"]}

WEEKDAY_HEADERS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


@dataclass
class CalendarTask:
    task_id: int
    title: str
    description: str
    start: date
    end: date
    category: str


@dataclass
class WeekSegment:
    task: CalendarTask
    start_col: int
    end_col: int
    lane: int
    continued_from_prev: bool
    continued_to_next: bool


def first_of_month(anchor: date) -> date:
    return anchor.replace(day=1)


def add_months(anchor: date, delta: int) -> date:
    month_index = anchor.month - 1 + delta
    year = anchor.year + month_index // 12
    month = month_index % 12 + 1
    return date(year, month, 1)


def last_of_month(anchor: date) -> date:
    return add_months(first_of_month(anchor), 1) - timedelta(days=1)


def build_month_matrix(anchor: date) -> List[List[date]]:
    month_start = first_of_month(anchor)
    month_end = last_of_month(anchor)
    grid_start = month_start - timedelta(days=month_start.weekday())
    weeks: List[List[date]] = []
    week_start = grid_start
    while week_start <= month_end:
        week = [week_start + timedelta(days=day_index) for day_index in range(7)]
        if any(day.month == month_start.month and day.year == month_start.year for day in week):
            weeks.append(week)
        week_start += timedelta(days=7)
    return weeks


def format_date_range(task: CalendarTask) -> str:
    same_day = task.start == task.end
    start_text = task.start.strftime("%d %b %Y")
    end_text = task.end.strftime("%d %b %Y")
    if same_day:
        return f"{task.start.strftime('%d %b %Y')}"
    return f"{start_text} → {end_text}"


def build_week_segments(week_dates: List[date], tasks: List[CalendarTask]) -> List[WeekSegment]:
    week_start = week_dates[0]
    week_end = week_dates[-1]
    candidates = []

    for task in tasks:
        task_start = task.start
        task_end = task.end
        if task_end < week_start or task_start > week_end:
            continue

        effective_start = max(task_start, week_start)
        effective_end = min(task_end, week_end)
        candidates.append(
            {
                "task": task,
                "start_col": (effective_start - week_start).days,
                "end_col": (effective_end - week_start).days,
                "continued_from_prev": task_start < week_start,
                "continued_to_next": task_end > week_end,
            }
        )

    candidates.sort(
        key=lambda item: (
            item["start_col"],
            -(item["end_col"] - item["start_col"]),
            item["task"].start,
        )
    )

    lane_last_end: List[int] = []
    segments: List[WeekSegment] = []
    for item in candidates:
        lane = -1
        for lane_index, last_end in enumerate(lane_last_end):
            if last_end < item["start_col"]:
                lane = lane_index
                lane_last_end[lane_index] = item["end_col"]
                break

        if lane == -1:
            lane = len(lane_last_end)
            lane_last_end.append(item["end_col"])

        segments.append(
            WeekSegment(
                task=item["task"],
                start_col=item["start_col"],
                end_col=item["end_col"],
                lane=lane,
                continued_from_prev=item["continued_from_prev"],
                continued_to_next=item["continued_to_next"],
            )
        )

    return segments


def calendar_global_stylesheet() -> str:
    return (
        "QWidget {"
        f"background: {COLOURS['bg0']};"
        f"color: {COLOURS['fg']};"
        "font-family: Inter, Segoe UI, Arial;"
        "}"
        "QToolTip {"
        f"background: {COLOURS['bg2']};"
        f"border: 1px solid {COLOURS['border']};"
        f"color: {COLOURS['fg']};"
        "padding: 8px;"
        "}"
    )


class TaskBarButton(QPushButton):
    edit_requested = pyqtSignal(object)

    def __init__(self, segment: WeekSegment, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.segment = segment
        task = segment.task
        prefix = "← " if segment.continued_from_prev else ""
        suffix = " →" if segment.continued_to_next else ""
        self.setText(f"{prefix}{task.title}{suffix}")
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(self._build_tooltip())
        self.setStyleSheet(
            "QPushButton {"
            f"background: {CATEGORY_STYLES.get(task.category, {'bg': 'rgba(68,71,90,0.5)'})['bg']};"
            f"border: 1px solid {CATEGORY_COLORS[task.category]};"
            f"color: {COLOURS['fg']};"
            "border-radius: 8px;"
            "padding: 4px 10px;"
            "text-align: left;"
            "font-size: 9px;"
            "font-weight: 600;"
            "}"
            "QPushButton:hover {"
            "background: rgba(68,71,90,0.92);"
            "}"
        )
        self.clicked.connect(lambda: self.edit_requested.emit(task.task_id))

    def _build_tooltip(self) -> str:
        task = self.segment.task
        return (
            f"<div style='color:{COLOURS['fg']};'>"
            f"<b>{task.title}</b><br>"
            f"{task.category}<br>"
            f"{format_date_range(task)}<br>"
            f"{task.description}"
            "</div>"
        )


class ClickableDayCell(QFrame):
    clicked = pyqtSignal(object)

    def __init__(self, day_value: date, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.day_value = day_value
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.day_value)
        super().mousePressEvent(event)


class WeekRowWidget(QFrame):
    edit_requested = pyqtSignal(object)
    add_requested = pyqtSignal(object)

    def __init__(
        self,
        week_dates: List[date],
        current_month: int,
        tasks: List[CalendarTask],
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.week_dates = week_dates
        self.current_month = current_month
        self.tasks = tasks
        self.segments = build_week_segments(week_dates, tasks)
        self.task_buttons: List[TaskBarButton] = []
        self.lane_height = 25
        self.setObjectName("weekRow")
        self.setStyleSheet(
            "#weekRow {"
            f"background: {COLOURS['bg0']};"
            f"border: 1px solid {COLOURS['border']};"
            "border-radius: 14px;"
            "}"
        )
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        day_grid = QGridLayout()
        day_grid.setContentsMargins(0, 0, 0, 0)
        day_grid.setHorizontalSpacing(5)
        day_grid.setVerticalSpacing(0)

        today = date.today()
        for index, day_value in enumerate(self.week_dates):
            cell = ClickableDayCell(day_value)
            cell.setMinimumHeight(28)
            is_today = day_value == today
            in_current_month = day_value.month == self.current_month
            cell.setStyleSheet(
                "QFrame {"
                f"background: {'rgba(98,114,164,0.22)' if is_today else 'rgba(33,34,44,0.95)'};"
                f"border: 1px solid {'#6272A4' if is_today else 'rgba(68,71,90,0.8)'};"
                "border-radius: 10px;"
                "}"
            )
            cell.clicked.connect(self.add_requested.emit)
            cell_layout = QVBoxLayout(cell)
            cell_layout.setContentsMargins(5, 5, 5, 5)
            cell_layout.setSpacing(2)

            day_label = QLabel(str(day_value.day))
            day_label.setFont(QFont("Inter", 10, QFont.Bold))
            day_label.setStyleSheet(
                f"color: {COLOURS['fg'] if in_current_month else 'rgba(248,248,242,0.45)'};"
                f"background-color: transparent;"
                f"border: none;"
            )
            cell_layout.addWidget(day_label)
            day_grid.addWidget(cell, 0, index)

        layout.addLayout(day_grid)

        lane_count = max(1, max((segment.lane for segment in self.segments), default=-1) + 1)
        overlay_height = max(25, lane_count * self.lane_height + 12)
        self.overlay_frame = QFrame()
        self.overlay_frame.setMinimumHeight(overlay_height)
        self.overlay_frame.setStyleSheet(
            "QFrame {"
            "background: transparent;"
            "border: 1px solid rgba(68,71,90,0.8);"
            "border-radius: 10px;"
            "}"
        )
        layout.addWidget(self.overlay_frame)

        if not self.segments:
            empty_label = QLabel("No tasks in this week")
            empty_label.setParent(self.overlay_frame)
            empty_label.move(12, 12)
            empty_label.setStyleSheet(f"color: {COLOURS['comment']}; font-size: 9px; background-color: transparent;"
                                      f"border: none;")
        else:
            for segment in self.segments:
                button = TaskBarButton(segment, self.overlay_frame)
                button.edit_requested.connect(self.edit_requested.emit)
                self.task_buttons.append(button)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not self.task_buttons:
            return

        available_width = max(1, self.overlay_frame.width() - 8)
        column_width = available_width / 7.0
        for button in self.task_buttons:
            segment = button.segment
            x = int(4 + segment.start_col * column_width)
            width = int((segment.end_col - segment.start_col + 1) * column_width - 8)
            y = 6 + segment.lane * self.lane_height
            button.setGeometry(x, y, max(70, width), 24)


class CalendarMonthView(QWidget):
    edit_requested = pyqtSignal(object)
    add_requested = pyqtSignal(object)

    def __init__(self, task_service, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.taskService = task_service
        self.current_month = first_of_month(date.today())
        self.tasks: List[CalendarTask] = []
        self.week_rows: List[WeekRowWidget] = []
        self._build_ui()

    def _build_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)

        header_layout = QGridLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setHorizontalSpacing(5)
        for index, label in enumerate(WEEKDAY_HEADERS):
            badge = QLabel(label)
            badge.setAlignment(Qt.AlignCenter)
            badge.setMinimumHeight(28)
            badge.setStyleSheet(
                f"background: transparent;"
                f"border: none;"
                f"color: {COLOURS['purple']};"
                "font-size: 10px;"
                "font-weight: 700;"
            )
            header_layout.addWidget(badge, 0, index)
        self.layout.addLayout(header_layout)

        self.rows_container = QWidget()
        self.rows_layout = QVBoxLayout(self.rows_container)
        self.rows_layout.setContentsMargins(0, 0, 0, 0)
        self.rows_layout.setSpacing(2)
        self.layout.addWidget(self.rows_container)

    def set_month_and_tasks(self, month_anchor: date, tasks: List[CalendarTask]):
        self.current_month = first_of_month(month_anchor)
        self.tasks = sorted(tasks, key=lambda item: (item.start, - (item.end - item.start).days))
        self._rebuild_rows()

    def _rebuild_rows(self):
        while self.rows_layout.count():
            item = self.rows_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        self.week_rows = []
        for week_dates in build_month_matrix(self.current_month):
            row = WeekRowWidget(week_dates, self.current_month.month, self.tasks)
            row.edit_requested.connect(self.edit_requested.emit)
            row.add_requested.connect(self.add_requested.emit)
            self.rows_layout.addWidget(row)
            self.week_rows.append(row)

        self.rows_layout.addStretch(1)
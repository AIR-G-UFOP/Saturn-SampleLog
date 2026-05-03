from dataclasses import dataclass
from datetime import date, timedelta
from typing import Dict, List, Optional

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
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


def build_month_matrix(anchor: date) -> List[List[date]]:
    month_start = first_of_month(anchor)
    grid_start = month_start - timedelta(days=month_start.weekday())
    weeks: List[List[date]] = []
    for week_index in range(6):
        week_start = grid_start + timedelta(days=week_index * 7)
        weeks.append([week_start + timedelta(days=day_index) for day_index in range(7)])
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


def create_sample_tasks(month_anchor: Optional[date] = None) -> List[CalendarTask]:
    anchor = first_of_month(month_anchor or date.today())

    def make_task(
        task_id: int,
        title: str,
        description: str,
        start_day: int,
        end_day: int,
        category: str,
    ) -> CalendarTask:
        style = CATEGORY_STYLES[category]
        return CalendarTask(
            task_id= task_id,
            title=title,
            description=description,
            start=date(anchor.year, anchor.month, start_day),
            end=date(anchor.year, anchor.month, end_day),
            category=category,
            color=style["color"],
        )

    return [
        make_task(1, "Analysis: U-Pb carbonate dating SMP001", "Mass spectrometer setup and instrument checks.", 3, 9, "analysis"),
        make_task(2, "Reduction: U-Pb carbonate dating SMP001", "Cross-team review of reduction output and anomalies.", 5, 10, "reduction"),
        make_task(3, "Client Handover", "Prepare report pack and final validation notes.", 9, 11,  "other"),
        make_task(4, "Thermal Study", "Document findings from chamber trial and compare baselines.", 12, 8, "other"),
        make_task(5, "Sample pre: SMP001", "Consumables and reagent stock reconciliation.", 18, 9, "sample_preparation"),
        make_task(6, "Analysis: trace elements SMP001", "A long-running process that continues into the final week.", 24, 10, "analysis"),
    ]


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
            f"border: 1px solid {task.color};"
            f"color: {COLOURS['fg']};"
            "border-radius: 8px;"
            "padding: 4px 10px;"
            "text-align: left;"
            "font-size: 11px;"
            "font-weight: 600;"
            "}"
            "QPushButton:hover {"
            "background: rgba(68,71,90,0.92);"
            "}"
        )
        self.clicked.connect(lambda: self.edit_requested.emit(task))

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
        self.lane_height = 35
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
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        day_grid = QGridLayout()
        day_grid.setContentsMargins(0, 0, 0, 0)
        day_grid.setHorizontalSpacing(8)
        day_grid.setVerticalSpacing(0)

        today = date.today()
        for index, day_value in enumerate(self.week_dates):
            cell = ClickableDayCell(day_value)
            cell.setMinimumHeight(46)
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
            cell_layout.setContentsMargins(10, 7, 10, 7)
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
        overlay_height = max(48, lane_count * self.lane_height + 12)
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
            empty_label.setStyleSheet(f"color: {COLOURS['comment']}; font-size: 11px; background-color: transparent;"
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
        header_layout.setHorizontalSpacing(8)
        for index, label in enumerate(WEEKDAY_HEADERS):
            badge = QLabel(label)
            badge.setAlignment(Qt.AlignCenter)
            badge.setMinimumHeight(28)
            badge.setStyleSheet(
                f"background: transparent;"
                f"border: none;"
                f"color: {COLOURS['purple']};"
                "font-size: 14px;"
                "font-weight: 700;"
            )
            header_layout.addWidget(badge, 0, index)
        self.layout.addLayout(header_layout)

        self.rows_container = QWidget()
        self.rows_layout = QVBoxLayout(self.rows_container)
        self.rows_layout.setContentsMargins(0, 0, 0, 0)
        self.rows_layout.setSpacing(5)
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



class CalendarStandalonePreview(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_month = first_of_month(date.today())
        self.events = create_sample_events(self.current_month)
        self.setWindowTitle("Continuous Calendar Preview")
        self.resize(1180, 900)
        self.setStyleSheet(calendar_global_stylesheet())
        self._build_ui()
        self._refresh_calendar()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(16)

        header_card = QFrame()
        header_card.setStyleSheet(
            "QFrame {"
            f"background: {DRACULA['bg1']};"
            f"border: 1px solid {DRACULA['border']};"
            "border-radius: 16px;"
            "}"
        )
        header_layout = QVBoxLayout(header_card)
        header_layout.setContentsMargins(18, 16, 18, 16)
        header_layout.setSpacing(6)

        title = QLabel("Calendar standalone preview")
        title.setFont(QFont("Inter", 15, QFont.Bold))
        subtitle = QLabel("Use this preview window to check the continuous calendar before embedding it.")
        subtitle.setStyleSheet(f"color: {DRACULA['muted']}; font-size: 11px;")
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        root.addWidget(header_card)

        controls_card = QFrame()
        controls_card.setStyleSheet(
            "QFrame {"
            f"background: {DRACULA['bg1']};"
            f"border: 1px solid {DRACULA['border']};"
            "border-radius: 16px;"
            "}"
        )
        controls_layout = QHBoxLayout(controls_card)
        controls_layout.setContentsMargins(16, 14, 16, 14)
        controls_layout.setSpacing(10)

        self.month_combo = QComboBox()
        self.year_combo = QComboBox()
        self.today_button = self._make_control_button("Today")

        self._style_combo_box(self.month_combo)
        self._style_combo_box(self.year_combo)
        self.month_combo.addItems([date(2000, month, 1).strftime("%B") for month in range(1, 13)])

        current_year = date.today().year
        for year in range(current_year - 10, current_year + 11):
            self.year_combo.addItem(str(year), year)

        month_label = QLabel("Month")
        month_label.setStyleSheet(f"color: {DRACULA['muted']}; font-size: 11px; font-weight: 600;")
        year_label = QLabel("Year")
        year_label.setStyleSheet(f"color: {DRACULA['muted']}; font-size: 11px; font-weight: 600;")

        controls_layout.addWidget(month_label)
        controls_layout.addWidget(self.month_combo, 1)
        controls_layout.addWidget(year_label)
        controls_layout.addWidget(self.year_combo)
        controls_layout.addWidget(self.today_button)
        root.addWidget(controls_card)

        self.calendar_view = CalendarMonthView()
        self.calendar_view.add_request.connect(self.handle_calendar_add)
        self.calendar_view.edit_requested.connect(self.handle_calendar_edit)
        self.calendar_view.delete_requested.connect(self.handle_calendar_delete)
        root.addWidget(self.calendar_view, 1)

        self.month_combo.currentIndexChanged.connect(self._handle_month_or_year_change)
        self.year_combo.currentIndexChanged.connect(self._handle_month_or_year_change)
        self.today_button.clicked.connect(self._jump_to_today)

        self._sync_controls_to_current_month()

    def _make_control_button(self, text: str) -> QPushButton:
        button = QPushButton(text)
        button.setCursor(Qt.PointingHandCursor)
        button.setMinimumHeight(38)
        button.setStyleSheet(
            "QPushButton {"
            f"background: {DRACULA['bg2']};"
            f"border: 1px solid {DRACULA['border']};"
            f"color: {DRACULA['fg']};"
            "border-radius: 10px;"
            "padding: 8px 14px;"
            "font-weight: 600;"
            "}"
            "QPushButton:hover {"
            f"background: {DRACULA['bg3']};"
            "}"
        )
        return button

    def _style_combo_box(self, combo: QComboBox):
        combo.setCursor(Qt.PointingHandCursor)
        combo.setMinimumHeight(38)
        combo.setStyleSheet(
            "QComboBox {"
            f"background: {DRACULA['bg2']};"
            f"border: 1px solid {DRACULA['border']};"
            f"color: {DRACULA['fg']};"
            "border-radius: 10px;"
            "padding: 8px 12px;"
            "font-weight: 600;"
            "}"
            "QComboBox:hover {"
            f"background: {DRACULA['bg3']};"
            "}"
            "QComboBox::drop-down {"
            "border: none;"
            "width: 28px;"
            "}"
            "QComboBox QAbstractItemView {"
            f"background: {DRACULA['bg2']};"
            f"border: 1px solid {DRACULA['border']};"
            f"color: {DRACULA['fg']};"
            "selection-background-color: rgba(98,114,164,0.35);"
            "selection-color: #F8F8F2;"
            "outline: 0;"
            "}"
        )

    def _sync_controls_to_current_month(self):
        self.month_combo.blockSignals(True)
        self.year_combo.blockSignals(True)
        self.month_combo.setCurrentIndex(self.current_month.month - 1)

        year_index = self.year_combo.findData(self.current_month.year)
        if year_index == -1:
            self.year_combo.addItem(str(self.current_month.year), self.current_month.year)
            year_index = self.year_combo.findData(self.current_month.year)
        self.year_combo.setCurrentIndex(year_index)

        self.month_combo.blockSignals(False)
        self.year_combo.blockSignals(False)

    def _handle_month_or_year_change(self):
        selected_month = self.month_combo.currentIndex() + 1
        selected_year = self.year_combo.currentData()
        if selected_year is None:
            return
        self.current_month = date(int(selected_year), selected_month, 1)
        self.events = create_sample_events(self.current_month)
        self._refresh_calendar()

    def _jump_to_today(self):
        self.current_month = first_of_month(date.today())
        self.events = create_sample_events(self.current_month)
        self._refresh_calendar()

    def _refresh_calendar(self):
        self._sync_controls_to_current_month()
        self.calendar_view.set_month_and_events(self.current_month, self.events)

    def _find_event(self, event_id: str) -> Optional[CalendarEvent]:
        return next((event for event in self.events if event.id == event_id), None)

    def handle_calendar_add(self, clicked_date: date):
        QMessageBox.information(
            self,
            "Add task",
            f"Preview only.\n\nAdd request received for: {clicked_date.strftime('%d %b %Y')}",
        )

    def handle_calendar_edit(self, event_id: str):
        event = self._find_event(event_id)
        if event is None:
            return
        QMessageBox.information(
            self,
            "Edit task",
            f"Preview only.\n\nTask: {event.title}\nWhen: {format_datetime_range(event)}",
        )

    def handle_calendar_delete(self, event_id: str):
        event = self._find_event(event_id)
        if event is None:
            return
        QMessageBox.information(
            self,
            "Delete task",
            f"Preview only.\n\nDelete request received for: {event.title}",
        )



def run_standalone_preview():
    app = QApplication.instance() or QApplication([])
    app.setStyleSheet(calendar_global_stylesheet())
    window = CalendarStandalonePreview()
    window.show()
    if QApplication.instance() is app:
        app.exec_()


if __name__ == "__main__":
    run_standalone_preview()

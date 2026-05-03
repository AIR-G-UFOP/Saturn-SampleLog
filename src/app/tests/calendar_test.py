from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Dict, List, Optional
from uuid import uuid4

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor, QFont
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

DRACULA: Dict[str, str] = {
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
    "Research": {"color": DRACULA["purple"], "bg": "rgba(189,147,249,0.18)"},
    "Analysis": {"color": DRACULA["cyan"], "bg": "rgba(139,233,253,0.18)"},
    "Meeting": {"color": DRACULA["orange"], "bg": "rgba(255,184,108,0.18)"},
    "Reduction": {"color": DRACULA["green"], "bg": "rgba(80,250,123,0.18)"},
    "Admin": {"color": DRACULA["pink"], "bg": "rgba(255,121,198,0.18)"},
}

WEEKDAY_HEADERS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


@dataclass
class CalendarEvent:
    id: str
    title: str
    description: str
    start: datetime
    end: datetime
    category: str
    color: str


@dataclass
class WeekSegment:
    event: CalendarEvent
    start_col: int
    end_col: int
    lane: int
    continued_from_prev: bool
    continued_to_next: bool


def start_of_day(value: datetime) -> datetime:
    return datetime.combine(value.date(), time.min)


def end_of_day(value: datetime) -> datetime:
    return datetime.combine(value.date(), time.max)


def first_of_month(anchor: date) -> date:
    return anchor.replace(day=1)


def last_of_month(anchor: date) -> date:
    return add_months(first_of_month(anchor), 1) - timedelta(days=1)


def add_months(anchor: date, delta: int) -> date:
    month_index = anchor.month - 1 + delta
    year = anchor.year + month_index // 12
    month = month_index % 12 + 1
    return date(year, month, 1)


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


def sort_events(events: List[CalendarEvent]) -> List[CalendarEvent]:
    return sorted(events, key=lambda item: (item.start, item.end, item.title.lower()))


def format_datetime_range(event: CalendarEvent) -> str:
    same_day = event.start.date() == event.end.date()
    start_text = event.start.strftime("%d %b %Y %H:%M")
    end_text = event.end.strftime("%d %b %Y %H:%M")
    if same_day:
        return f"{event.start.strftime('%d %b %Y')} • {event.start.strftime('%H:%M')}–{event.end.strftime('%H:%M')}"
    return f"{start_text} → {end_text}"


def build_week_segments(week_dates: List[date], events: List[CalendarEvent]) -> List[WeekSegment]:
    week_start = week_dates[0]
    week_end = week_dates[-1]
    candidates = []

    for event in events:
        event_start = event.start.date()
        event_end = event.end.date()
        if event_end < week_start or event_start > week_end:
            continue

        effective_start = max(event_start, week_start)
        effective_end = min(event_end, week_end)
        candidates.append(
            {
                "event": event,
                "start_col": (effective_start - week_start).days,
                "end_col": (effective_end - week_start).days,
                "continued_from_prev": event_start < week_start,
                "continued_to_next": event_end > week_end,
            }
        )

    candidates.sort(
        key=lambda item: (
            item["start_col"],
            -(item["end_col"] - item["start_col"]),
            item["event"].start,
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
                event=item["event"],
                start_col=item["start_col"],
                end_col=item["end_col"],
                lane=lane,
                continued_from_prev=item["continued_from_prev"],
                continued_to_next=item["continued_to_next"],
            )
        )

    return segments


class EventHoverCard(QFrame):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent, Qt.ToolTip | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setObjectName("eventHoverCard")
        self.setStyleSheet(
            "#eventHoverCard {"
            f"background: {DRACULA['bg1']};"
            f"border: 1px solid {DRACULA['border']};"
            "border-radius: 16px;"
            "}"
        )
        self.setFixedWidth(320)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        self.category_badge = QLabel()
        self.category_badge.setAlignment(Qt.AlignCenter)
        self.category_badge.setFixedHeight(24)
        self.category_badge.setMinimumWidth(84)

        self.title_label = QLabel()
        self.title_label.setWordWrap(True)
        self.title_label.setFont(QFont("Inter", 12, QFont.Bold))
        self.title_label.setStyleSheet(f"color: {DRACULA['fg']};")

        self.time_label = QLabel()
        self.time_label.setWordWrap(True)
        self.time_label.setStyleSheet(f"color: {DRACULA['cyan']}; font-size: 11px; font-weight: 600;")

        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet(f"color: {DRACULA['muted']}; font-size: 11px;")

        self.footer_label = QLabel("Left click to edit • Right click for more actions")
        self.footer_label.setWordWrap(True)
        self.footer_label.setStyleSheet(f"color: {DRACULA['comment']}; font-size: 10px;")

        layout.addWidget(self.category_badge, 0, Qt.AlignLeft)
        layout.addWidget(self.title_label)
        layout.addWidget(self.time_label)
        layout.addWidget(self.description_label)
        layout.addSpacing(2)
        layout.addWidget(self.footer_label)

    def set_event(self, event: CalendarEvent):
        style = CATEGORY_STYLES.get(event.category, {"color": DRACULA['purple'], "bg": "rgba(189,147,249,0.18)"})
        self.category_badge.setText(event.category.upper())
        self.category_badge.setStyleSheet(
            "padding: 2px 10px; border-radius: 12px; font-size: 11px; font-weight: 700;"
            f"background: {style['bg']};"
            f"border: 1px solid {style['color']};"
            f"color: {style['color']};"
        )
        self.title_label.setText(event.title)
        self.time_label.setText(format_datetime_range(event))
        self.description_label.setText(event.description or "No extra details")
        self.adjustSize()


def calendar_global_stylesheet() -> str:
    return (
        "QWidget {"
        f"background: {DRACULA['bg0']};"
        f"color: {DRACULA['fg']};"
        "font-family: Inter, Segoe UI, Arial;"
        "}"
        "QToolTip {"
        f"background: {DRACULA['bg2']};"
        f"border: 1px solid {DRACULA['border']};"
        f"color: {DRACULA['fg']};"
        "padding: 8px;"
        "}"
    )


def create_sample_events(month_anchor: Optional[date] = None) -> List[CalendarEvent]:
    anchor = first_of_month(month_anchor or date.today())

    def make_event(
        title: str,
        description: str,
        month_offset: int,
        start_day: int,
        start_hour: int,
        end_day: int,
        end_hour: int,
        category: str,
    ) -> CalendarEvent:
        month_anchor_date = add_months(anchor, month_offset)
        style = CATEGORY_STYLES[category]
        return CalendarEvent(
            id=str(uuid4()),
            title=title,
            description=description,
            start=datetime(month_anchor_date.year, month_anchor_date.month, start_day, start_hour, 0),
            end=datetime(month_anchor_date.year, month_anchor_date.month, end_day, end_hour, 0),
            category=category,
            color=style["color"],
        )

    return sort_events(
        [
            make_event("Archive Review", "Prepare the previous month archive for audit sign-off.", -1, 26, 9, 28, 14, "Admin"),
            make_event("Calibration Run", "Mass spectrometer setup and instrument checks.", 0, 3, 9, 3, 12, "Analysis"),
            make_event("Soil Batch Review", "Cross-team review of reduction output and anomalies.", 0, 5, 10, 8, 16, "Reduction"),
            make_event("Client Handover", "Prepare report pack and final validation notes.", 0, 9, 11, 13, 15, "Meeting"),
            make_event("Thermal Study", "Document findings from chamber trial and compare baselines.", 0, 12, 8, 19, 17, "Research"),
            make_event("Inventory Audit", "Consumables and reagent stock reconciliation.", 0, 18, 9, 20, 13, "Admin"),
            make_event("Late Span Task", "A long-running process that continues into the final week.", 0, 24, 10, 29, 15, "Analysis"),
            make_event("Cross-site Review", "Coordinate next month opening tasks across laboratory teams.", 1, 4, 10, 7, 16, "Meeting"),
            make_event("Method Validation", "Run the first validation pass for the incoming sample series.", 1, 11, 8, 15, 17, "Research"),
        ]
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


class EventBarButton(QPushButton):
    edit_requested = pyqtSignal(str)
    delete_requested = pyqtSignal(str)
    hover_card: Optional[EventHoverCard] = None

    def __init__(self, segment: WeekSegment, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.segment = segment
        event = segment.event
        prefix = "◀ " if segment.continued_from_prev else ""
        suffix = " ▶" if segment.continued_to_next else ""
        self.setText(f"{prefix}{event.title}{suffix}")
        self.setCursor(Qt.PointingHandCursor)
        self.setMouseTracking(True)
        self.setStyleSheet(
            "QPushButton {"
            f"background: {CATEGORY_STYLES.get(event.category, {'bg': 'rgba(68,71,90,0.5)'})['bg']};"
            f"border: 1px solid {event.color};"
            f"color: {DRACULA['fg']};"
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
        self.clicked.connect(lambda: self.edit_requested.emit(event.id))

    @classmethod
    def _get_hover_card(cls) -> EventHoverCard:
        if cls.hover_card is None:
            cls.hover_card = EventHoverCard()
        return cls.hover_card

    def _show_hover_card(self):
        card = self._get_hover_card()
        card.set_event(self.segment.event)
        global_pos = self.mapToGlobal(self.rect().bottomLeft())
        card.move(global_pos.x(), global_pos.y() + 8)
        card.show()
        card.raise_()

    def _hide_hover_card(self):
        self._get_hover_card().hide()

    def enterEvent(self, event):
        self._show_hover_card()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hide_hover_card()
        super().leaveEvent(event)

    def mouseMoveEvent(self, event):
        card = self._get_hover_card()
        if card.isVisible():
            global_pos = self.mapToGlobal(self.rect().bottomLeft())
            card.move(global_pos.x(), global_pos.y() + 8)
        super().mouseMoveEvent(event)

    def contextMenuEvent(self, event):
        self._hide_hover_card()
        menu = QMenu(self)
        menu.setStyleSheet(
            "QMenu {"
            f"background: {DRACULA['bg2']};"
            f"border: 1px solid {DRACULA['border']};"
            f"color: {DRACULA['fg']};"
            "padding: 6px;"
            "}"
            "QMenu::item {"
            "padding: 6px 18px;"
            "border-radius: 6px;"
            "}"
            "QMenu::item:selected {"
            f"background: {DRACULA['bg3']};"
            "}"
        )
        edit_action = menu.addAction("Edit task")
        delete_action = menu.addAction("Delete task")
        chosen = menu.exec_(QCursor.pos())
        if chosen == edit_action:
            self.edit_requested.emit(self.segment.event.id)
        elif chosen == delete_action:
            self.delete_requested.emit(self.segment.event.id)

    def hideEvent(self, event):
        self._hide_hover_card()
        super().hideEvent(event)


class TaskListItem(QFrame):
    navigate_requested = pyqtSignal(str)
    edit_requested = pyqtSignal(str)
    delete_requested = pyqtSignal(str)

    def __init__(self, event: CalendarEvent, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.event_data = event
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(
            "QFrame {"
            f"background: {DRACULA['bg1']};"
            f"border: 1px solid {DRACULA['border']};"
            "border-radius: 14px;"
            "}"
            "QFrame:hover {"
            f"background: {DRACULA['bg2']};"
            "}"
        )
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(12)

        accent = QFrame()
        accent.setFixedWidth(5)
        accent.setStyleSheet(
            f"background: {self.event_data.color}; border: none; border-radius: 2px;"
        )
        layout.addWidget(accent)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(4)

        title = QLabel(self.event_data.title)
        title.setFont(QFont("Inter", 11, QFont.Bold))
        title.setStyleSheet(f"color: {DRACULA['fg']};")

        meta = QLabel(
            f"{self.event_data.category} • {format_datetime_range(self.event_data)}"
        )
        meta.setStyleSheet(f"color: {DRACULA['muted']}; font-size: 11px;")

        description = QLabel(self.event_data.description)
        description.setWordWrap(True)
        description.setStyleSheet(f"color: {DRACULA['comment']}; font-size: 10px;")

        content_layout.addWidget(title)
        content_layout.addWidget(meta)
        content_layout.addWidget(description)
        layout.addLayout(content_layout, 1)

        actions_layout = QVBoxLayout()
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(8)

        self.go_button = self._make_action_button("Go to month")
        self.edit_button = self._make_action_button("Edit")
        self.delete_button = self._make_action_button("Delete", destructive=True)

        self.go_button.clicked.connect(lambda: self.navigate_requested.emit(self.event_data.id))
        self.edit_button.clicked.connect(lambda: self.edit_requested.emit(self.event_data.id))
        self.delete_button.clicked.connect(lambda: self.delete_requested.emit(self.event_data.id))

        actions_layout.addWidget(self.go_button)
        actions_layout.addWidget(self.edit_button)
        actions_layout.addWidget(self.delete_button)
        actions_layout.addStretch(1)
        layout.addLayout(actions_layout)

    def _make_action_button(self, text: str, destructive: bool = False) -> QPushButton:
        button = QPushButton(text)
        button.setCursor(Qt.PointingHandCursor)
        button.setMinimumHeight(30)
        button.setStyleSheet(
            "QPushButton {"
            f"background: {'rgba(255,85,85,0.16)' if destructive else DRACULA['bg2']};"
            f"border: 1px solid {DRACULA['red'] if destructive else DRACULA['border']};"
            f"color: {DRACULA['red'] if destructive else DRACULA['fg']};"
            "border-radius: 8px;"
            "padding: 4px 12px;"
            "font-size: 11px;"
            "font-weight: 600;"
            "}"
            "QPushButton:hover {"
            f"background: {'rgba(255,85,85,0.24)' if destructive else DRACULA['bg3']};"
            "}"
        )
        return button

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.navigate_requested.emit(self.event_data.id)
        super().mousePressEvent(event)


class WeekRowWidget(QFrame):
    add_request = pyqtSignal(object)
    edit_requested = pyqtSignal(str)
    delete_requested = pyqtSignal(str)

    def __init__(
        self,
        week_dates: List[date],
        current_month: int,
        events: List[CalendarEvent],
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.week_dates = week_dates
        self.current_month = current_month
        self.events = events
        self.segments = build_week_segments(week_dates, events)
        self.event_buttons: List[EventBarButton] = []
        self.lane_height = 28
        self.setObjectName("weekRow")
        self.setStyleSheet(
            "#weekRow {"
            f"background: {DRACULA['bg0']};"
            f"border: 1px solid {DRACULA['border']};"
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
            cell.clicked.connect(self.add_request.emit)
            cell_layout = QVBoxLayout(cell)
            cell_layout.setContentsMargins(10, 7, 10, 7)
            cell_layout.setSpacing(2)

            day_label = QLabel(str(day_value.day))
            day_label.setFont(QFont("Inter", 10, QFont.Bold))
            day_label.setStyleSheet(
                f"color: {DRACULA['fg'] if in_current_month else 'rgba(248,248,242,0.45)'};"
            )
            cell_layout.addWidget(day_label)

            event_count = sum(1 for item in self.events if item.start.date() <= day_value <= item.end.date())
            count_label = QLabel(f"{event_count} task{'s' if event_count != 1 else ''}")
            count_label.setStyleSheet(f"color: {DRACULA['comment']}; font-size: 10px;")
            cell_layout.addWidget(count_label)
            day_grid.addWidget(cell, 0, index)

        layout.addLayout(day_grid)

        lane_count = max(1, max((segment.lane for segment in self.segments), default=-1) + 1)
        overlay_height = max(48, lane_count * self.lane_height + 12)
        self.overlay_frame = QFrame()
        self.overlay_frame.setMinimumHeight(overlay_height)
        self.overlay_frame.setStyleSheet(
            "QFrame {"
            "background: qlineargradient(x1:0,y1:0,x2:0,y2:1,"
            "stop:0 rgba(40,42,54,0.95), stop:1 rgba(31,34,48,0.72));"
            "border: 1px solid rgba(68,71,90,0.8);"
            "border-radius: 10px;"
            "}"
        )
        layout.addWidget(self.overlay_frame)

        if not self.segments:
            empty_label = QLabel("No tasks in this week")
            empty_label.setParent(self.overlay_frame)
            empty_label.move(12, 12)
            empty_label.setStyleSheet(f"color: {DRACULA['comment']}; font-size: 11px;")
        else:
            for segment in self.segments:
                button = EventBarButton(segment, self.overlay_frame)
                button.edit_requested.connect(self.edit_requested.emit)
                button.delete_requested.connect(self.delete_requested.emit)
                self.event_buttons.append(button)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not self.event_buttons:
            return

        available_width = max(1, self.overlay_frame.width() - 8)
        column_width = available_width / 7.0
        for button in self.event_buttons:
            segment = button.segment
            x = int(4 + segment.start_col * column_width)
            width = int((segment.end_col - segment.start_col + 1) * column_width - 8)
            y = 6 + segment.lane * self.lane_height
            button.setGeometry(x, y, max(70, width), 24)


class CalendarMonthView(QWidget):
    add_request = pyqtSignal(object)
    edit_requested = pyqtSignal(str)
    delete_requested = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.current_month = first_of_month(date.today())
        self.events: List[CalendarEvent] = []
        self.week_rows: List[WeekRowWidget] = []
        self._build_ui()

    def _build_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(10)

        header_layout = QGridLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setHorizontalSpacing(8)
        for index, label in enumerate(WEEKDAY_HEADERS):
            badge = QLabel(label)
            badge.setAlignment(Qt.AlignCenter)
            badge.setMinimumHeight(28)
            badge.setStyleSheet(
                f"background: {DRACULA['bg1']};"
                f"border: 1px solid {DRACULA['border']};"
                "border-radius: 8px;"
                f"color: {DRACULA['muted']};"
                "font-size: 11px;"
                "font-weight: 700;"
            )
            header_layout.addWidget(badge, 0, index)
        self.layout.addLayout(header_layout)

        self.rows_container = QWidget()
        self.rows_layout = QVBoxLayout(self.rows_container)
        self.rows_layout.setContentsMargins(0, 0, 0, 0)
        self.rows_layout.setSpacing(10)
        self.layout.addWidget(self.rows_container)

    def set_month_and_events(self, month_anchor: date, events: List[CalendarEvent]):
        self.current_month = first_of_month(month_anchor)
        self.events = sorted(events, key=lambda item: (item.start, -(item.end - item.start).days))
        self._rebuild_rows()

    def _rebuild_rows(self):
        while self.rows_layout.count():
            item = self.rows_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        self.week_rows = []
        for week_dates in build_month_matrix(self.current_month):
            row = WeekRowWidget(week_dates, self.current_month.month, self.events)
            row.add_request.connect(self.add_request.emit)
            row.edit_requested.connect(self.edit_requested.emit)
            row.delete_requested.connect(self.delete_requested.emit)
            self.rows_layout.addWidget(row)
            self.week_rows.append(row)

        self.rows_layout.addStretch(1)


class CalendarStandalonePreview(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_month = first_of_month(date.today())
        self.events = create_sample_events(self.current_month)
        self.task_cards: List[TaskListItem] = []
        self.setWindowTitle("Continuous Calendar Preview")
        self.resize(1180, 980)
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

        tasks_card = QFrame()
        tasks_card.setStyleSheet(
            "QFrame {"
            f"background: {DRACULA['bg1']};"
            f"border: 1px solid {DRACULA['border']};"
            "border-radius: 16px;"
            "}"
        )
        tasks_layout = QVBoxLayout(tasks_card)
        tasks_layout.setContentsMargins(16, 14, 16, 14)
        tasks_layout.setSpacing(12)

        tasks_header_layout = QHBoxLayout()
        tasks_header_layout.setContentsMargins(0, 0, 0, 0)
        tasks_header_layout.setSpacing(8)

        tasks_title = QLabel("All tasks")
        tasks_title.setFont(QFont("Inter", 12, QFont.Bold))
        tasks_subtitle = QLabel("Sorted by date. Click a task to jump to its month.")
        tasks_subtitle.setStyleSheet(f"color: {DRACULA['muted']}; font-size: 11px;")

        tasks_header_text = QVBoxLayout()
        tasks_header_text.setContentsMargins(0, 0, 0, 0)
        tasks_header_text.setSpacing(2)
        tasks_header_text.addWidget(tasks_title)
        tasks_header_text.addWidget(tasks_subtitle)
        tasks_header_layout.addLayout(tasks_header_text)
        tasks_header_layout.addStretch(1)
        tasks_layout.addLayout(tasks_header_layout)

        self.tasks_scroll = QScrollArea()
        self.tasks_scroll.setWidgetResizable(True)
        self.tasks_scroll.setFrameShape(QFrame.NoFrame)
        self.tasks_scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
            "QScrollBar:vertical {"
            f"background: {DRACULA['bg0']};"
            "width: 10px;"
            "margin: 0px;"
            "border-radius: 5px;"
            "}"
            "QScrollBar::handle:vertical {"
            f"background: {DRACULA['border']};"
            "min-height: 28px;"
            "border-radius: 5px;"
            "}"
            "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }"
        )

        self.tasks_container = QWidget()
        self.tasks_list_layout = QVBoxLayout(self.tasks_container)
        self.tasks_list_layout.setContentsMargins(0, 0, 0, 0)
        self.tasks_list_layout.setSpacing(10)
        self.tasks_scroll.setWidget(self.tasks_container)
        tasks_layout.addWidget(self.tasks_scroll)
        root.addWidget(tasks_card, 1)

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
        self._refresh_calendar()

    def _jump_to_today(self):
        self.current_month = first_of_month(date.today())
        self._refresh_calendar()

    def _refresh_calendar(self):
        self._sync_controls_to_current_month()
        self.calendar_view.set_month_and_events(self.current_month, self.events)
        self._refresh_task_list()

    def _refresh_task_list(self):
        while self.tasks_list_layout.count():
            item = self.tasks_list_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        self.task_cards = []
        sorted_events = sort_events(self.events)
        if not sorted_events:
            empty_label = QLabel("No tasks loaded")
            empty_label.setStyleSheet(f"color: {DRACULA['muted']}; font-size: 11px;")
            self.tasks_list_layout.addWidget(empty_label)
            self.tasks_list_layout.addStretch(1)
            return

        for event in sorted_events:
            card = TaskListItem(event)
            card.navigate_requested.connect(self.handle_task_focus_request)
            card.edit_requested.connect(self.handle_calendar_edit)
            card.delete_requested.connect(self.handle_calendar_delete)
            self.tasks_list_layout.addWidget(card)
            self.task_cards.append(card)

        self.tasks_list_layout.addStretch(1)

    def _find_event(self, event_id: str) -> Optional[CalendarEvent]:
        return next((event for event in self.events if event.id == event_id), None)

    def handle_task_focus_request(self, event_id: str):
        event = self._find_event(event_id)
        if event is None:
            return
        self.current_month = first_of_month(event.start.date())
        self._refresh_calendar()

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
    EventBarButton.hover_card = None
    app = QApplication.instance() or QApplication([])
    app.setStyleSheet(calendar_global_stylesheet())
    window = CalendarStandalonePreview()
    window.show()
    if QApplication.instance() is app:
        app.exec_()


if __name__ == "__main__":
    run_standalone_preview()

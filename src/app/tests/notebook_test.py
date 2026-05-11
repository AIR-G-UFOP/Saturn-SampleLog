from dataclasses import dataclass
from typing import Dict, List, Optional

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QTextCharFormat, QTextCursor
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

DRACULA: Dict[str, str] = {
    "bg0": "#171821",
    "bg1": "#1F2230",
    "bg2": "#282A36",
    "bg3": "#343746",
    "border": "#454A61",
    "fg": "#F8F8F2",
    "muted": "#AAB2D5",
    "white_page": "#FBFBFD",
    "white_ink": "#1F2230",
    "purple": "#BD93F9",
    "pink": "#FF79C6",
    "cyan": "#8BE9FD",
    "green": "#50FA7B",
    "yellow": "#F1FA8C",
    "orange": "#FFB86C",
    "red": "#FF5555",
}


@dataclass
class MentionItem:
    id: str
    label: str
    caption: str
    token: str


@dataclass
class NotebookPage:
    id: str
    title: str
    summary: str
    content: str


@dataclass
class NotebookRecord:
    id: str
    title: str
    subtitle: str
    pages: List[NotebookPage]


@dataclass
class MentionSection:
    title: str
    icon: str
    accent: str
    items: List[MentionItem]


def build_initial_collections() -> Dict[str, List[NotebookRecord]]:
    return {
        "notebook": [
            NotebookRecord(
                id="zircon-dating",
                title="Zircon Dating",
                subtitle="Age model notes",
                pages=[
                    NotebookPage(
                        id="prep-notes",
                        title="Preparation Notes",
                        summary="Mount preparation, standards, and sample intake notes.",
                        content=(
                            "<h1>Preparation Notes</h1>"
                            "<p>Select linked items on the right to mention users, samples, analyses, or reductions.</p>"
                            "<p>Use this page for draft methods, contextual notes, and cross-linked laboratory knowledge.</p>"
                        ),
                    ),
                    NotebookPage(
                        id="run-03",
                        title="Titanite Run 03",
                        summary="Reduction narrative and linked U-Pb session context.",
                        content=(
                            "<h1>Titanite Run 03</h1>"
                            "<p>Reduction generated with <strong>@Reduction: U-Pb_2026</strong>.</p>"
                            "<p>Summarize the sequence, observations, flagged spots, and reviewer notes here.</p>"
                        ),
                    ),
                ],
            ),
            NotebookRecord(
                id="carbonate-upb",
                title="Carbonate U-Pb",
                subtitle="Session planning",
                pages=[
                    NotebookPage(
                        id="screening-plan",
                        title="Screening Plan",
                        summary="Reference material order, expected dates, and priority batches.",
                        content=(
                            "<h1>Screening Plan</h1>"
                            "<p>Outline the planned order of work, key users, and referenced analyses.</p>"
                        ),
                    ),
                    NotebookPage(
                        id="report-draft",
                        title="Report Draft",
                        summary="Draft client-facing reduction summary and observations.",
                        content=(
                            "<h1>Report Draft</h1>"
                            "<p>Collect the final interpretation points, QA notes, and linked data reductions here.</p>"
                        ),
                    ),
                ],
            ),
            NotebookRecord(
                id="weekly-methods",
                title="Weekly Methods",
                subtitle="Reference library",
                pages=[
                    NotebookPage(
                        id="laser-settings",
                        title="Laser Settings",
                        summary="Shared operating settings and accepted tuning ranges.",
                        content=(
                            "<h1>Laser Settings</h1>"
                            "<p>Keep stable operational settings, calibration notes, and troubleshooting references in this page.</p>"
                        ),
                    )
                ],
            ),
        ],
        "log": [
            NotebookRecord(
                id="daily-lab-log",
                title="Daily Lab Log",
                subtitle="Operational activity",
                pages=[
                    NotebookPage(
                        id="monday-shift",
                        title="Monday Shift",
                        summary="Open actions, sample intake, and instrumentation status.",
                        content=(
                            "<h1>Monday Shift</h1>"
                            "<p>Capture instrument status, urgent requests, and who is handling each task.</p>"
                        ),
                    ),
                    NotebookPage(
                        id="maintenance-log",
                        title="Maintenance Log",
                        summary="Preventive maintenance and service notes.",
                        content=(
                            "<h1>Maintenance Log</h1>"
                            "<p>Record parts replaced, service windows, and follow-up actions.</p>"
                        ),
                    ),
                ],
            ),
            NotebookRecord(
                id="incoming-requests",
                title="Incoming Requests",
                subtitle="Client queue",
                pages=[
                    NotebookPage(
                        id="priority-intake",
                        title="Priority Intake",
                        summary="Samples and analyses waiting for triage.",
                        content=(
                            "<h1>Priority Intake</h1>"
                            "<p>Document high-priority users, sample codes, and handoff notes for the team.</p>"
                        ),
                    )
                ],
            ),
        ],
    }


def build_initial_mentions() -> List[MentionSection]:
    return [
        MentionSection(
            title="Users",
            icon="👥",
            accent=DRACULA["cyan"],
            items=[
                MentionItem("user-1", "Dr. Sarah Patel", "Lead analyst", "@User: Sarah_Patel"),
                MentionItem("user-2", "Marco Silva", "Sample coordinator", "@User: Marco_Silva"),
                MentionItem("user-3", "Helen Ward", "Reduction reviewer", "@User: Helen_Ward"),
            ],
        ),
        MentionSection(
            title="Samples",
            icon="🧪",
            accent=DRACULA["purple"],
            items=[
                MentionItem("sample-1", "Zircon_001", "Mount A / tray 4", "@Sample: Zircon_001"),
                MentionItem("sample-2", "Titanite_003", "Polished grain mount", "@Sample: Titanite_003"),
                MentionItem("sample-3", "Carb_112", "Carbonate session batch", "@Sample: Carb_112"),
            ],
        ),
        MentionSection(
            title="Analyses",
            icon="📊",
            accent=DRACULA["yellow"],
            items=[
                MentionItem("analysis-1", "LAICPMS_Run_04", "Session in progress", "@Analysis: LAICPMS_Run_04"),
                MentionItem("analysis-2", "Imaging_Scan_12", "CL imaging", "@Analysis: Imaging_Scan_12"),
                MentionItem("analysis-3", "Spot_Check_19", "Quality control", "@Analysis: Spot_Check_19"),
            ],
        ),
        MentionSection(
            title="Data reductions",
            icon="🔗",
            accent=DRACULA["orange"],
            items=[
                MentionItem("reduction-1", "U-Pb_2026", "Validated reduction", "@Reduction: U-Pb_2026"),
                MentionItem("reduction-2", "Titanite_QA", "Review pending", "@Reduction: Titanite_QA"),
                MentionItem("reduction-3", "Session_Beta", "Preliminary draft", "@Reduction: Session_Beta"),
            ],
        ),
    ]


class SidebarModeButton(QPushButton):
    def __init__(self, label: str, icon_text: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setText(f"{icon_text}  {label}")
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(58)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.set_active(False)

    def set_active(self, active: bool):
        border_color = "#6F79AC" if active else DRACULA["border"]
        bg_color = "rgba(98,114,164,0.18)" if active else DRACULA["bg0"]
        text_color = DRACULA["pink"] if active else DRACULA["fg"]
        self.setStyleSheet(
            "QPushButton {"
            f"background: {bg_color};"
            f"border: 1px solid {border_color};"
            "border-radius: 14px;"
            "padding: 12px 14px;"
            f"color: {text_color};"
            "text-align: left;"
            "font-size: 13px;"
            "font-weight: 600;"
            "}"
            "QPushButton:hover {"
            f"background: {DRACULA['bg3']};"
            "}"
        )


class InfoMetric(QFrame):
    def __init__(self, label: str, value: str, accent: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._accent = accent
        self.label_widget = QLabel(label)
        self.value_widget = QLabel(value)
        self.value_widget.setObjectName("metricValue")
        self.setStyleSheet(
            "QFrame {"
            f"background: transparent;"
            f"border: 1px solid {DRACULA['border']};"
            "border-radius: 12px;"
            "}"
            f"QLabel {{ color: {DRACULA['muted']}; font-size: 12px; }}"
            f"QLabel#metricValue {{ color: {self._accent}; font-size: 13px; font-weight: 700; }}"
        )
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)
        layout.addWidget(self.label_widget)
        layout.addStretch(1)
        layout.addWidget(self.value_widget)

    def set_value(self, value: str):
        self.value_widget.setText(value)


class CollapsibleCard(QFrame):
    toggled = pyqtSignal(bool)

    def __init__(
        self,
        title: str,
        subtitle: str,
        accent: str,
        action_label: Optional[str] = None,
        icon_text: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.title = title
        self.subtitle = subtitle
        self.accent = accent
        self.is_open = True
        self.content_widget: Optional[QWidget] = None
        self.setStyleSheet(
            "QFrame {"
            f"background: {DRACULA['bg1']};"
            f"border: 1px solid {DRACULA['border']};"
            "border-radius: 22px;"
            "}"
        )

        self.root_layout = QVBoxLayout(self)
        self.root_layout.setContentsMargins(14, 14, 14, 14)
        self.root_layout.setSpacing(12)

        header = QHBoxLayout()
        header.setContentsMargins(2, 0, 2, 0)
        header.setSpacing(10)

        left = QHBoxLayout()
        left.setContentsMargins(0, 0, 0, 0)
        left.setSpacing(10)

        if icon_text:
            badge = QLabel(icon_text)
            badge.setAlignment(Qt.AlignCenter)
            badge.setFixedSize(36, 36)
            badge.setStyleSheet(
                f"background: {DRACULA['bg0']};"
                f"border: 1px solid {DRACULA['border']};"
                "border-radius: 12px;"
                f"color: {self.accent};"
                "font-size: 16px;"
            )
            left.addWidget(badge)

        text_stack = QVBoxLayout()
        text_stack.setContentsMargins(0, 0, 0, 0)
        text_stack.setSpacing(2)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"color: {DRACULA['fg']}; font-size: 14px; font-weight: 700;")
        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setStyleSheet(f"color: {DRACULA['muted']}; font-size: 11px;")
        text_stack.addWidget(self.title_label)
        text_stack.addWidget(self.subtitle_label)
        left.addLayout(text_stack)
        header.addLayout(left, 1)

        self.action_button: Optional[QPushButton]
        if action_label:
            self.action_button = QPushButton(action_label)
            self.action_button.setCursor(Qt.PointingHandCursor)
            self.action_button.setMinimumHeight(30)
            self.action_button.setStyleSheet(
                "QPushButton {"
                f"background: {DRACULA['bg2']};"
                f"border: 1px solid {DRACULA['border']};"
                f"color: {DRACULA['fg']};"
                "border-radius: 10px;"
                "padding: 4px 12px;"
                "font-size: 11px;"
                "font-weight: 600;"
                "}"
                "QPushButton:hover {"
                f"background: {DRACULA['bg3']};"
                "}"
            )
            header.addWidget(self.action_button)
        else:
            self.action_button = None

        self.toggle_button = QToolButton()
        self.toggle_button.setText("▾")
        self.toggle_button.setCursor(Qt.PointingHandCursor)
        self.toggle_button.setAutoRaise(True)
        self.toggle_button.clicked.connect(self.toggle_open)
        self.toggle_button.setStyleSheet(
            "QToolButton {"
            f"background: transparent;"
            f"color: {DRACULA['fg']};"
            "border: none;"
            "font-size: 16px;"
            "padding: 4px;"
            "}"
            "QToolButton:hover {"
            f"background: {DRACULA['bg3']};"
            "border-radius: 8px;"
            "}"
        )
        header.addWidget(self.toggle_button)
        self.root_layout.addLayout(header)

    def set_title(self, title: str):
        self.title = title
        self.title_label.setText(title)

    def set_content_widget(self, widget: QWidget):
        self.content_widget = widget
        self.root_layout.addWidget(widget)

    def set_open(self, open_state: bool):
        self.is_open = open_state
        self.toggle_button.setText("▾" if open_state else "▸")
        if self.content_widget is not None:
            self.content_widget.setVisible(open_state)
        if self.action_button is not None:
            self.action_button.setVisible(open_state)
        self.toggled.emit(open_state)

    def toggle_open(self):
        self.set_open(not self.is_open)


class ListItemButton(QPushButton):
    def __init__(self, title: str, subtitle: str, accent: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.accent = accent
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(78)
        self.setText(f"{title}\n{subtitle}")
        self._apply_style(False)

    def _apply_style(self, selected: bool):
        border_color = self.accent if selected else DRACULA["border"]
        background = "rgba(98,114,164,0.18)" if selected else DRACULA["bg0"]
        self.setStyleSheet(
            "QPushButton {"
            f"background: {background};"
            f"border: 1px solid {border_color};"
            "border-radius: 14px;"
            "padding: 12px 14px;"
            f"color: {DRACULA['fg']};"
            "text-align: left;"
            "font-size: 13px;"
            "font-weight: 600;"
            "}"
            "QPushButton:hover {"
            f"background: {DRACULA['bg3']};"
            "padding-left: 16px;"
            "}"
        )

    def setChecked(self, checked: bool):
        super().setChecked(checked)
        self._apply_style(checked)


class ListPanel(CollapsibleCard):
    selection_changed = pyqtSignal(str)

    def __init__(self, title: str, action_label: str, accent: str, parent: Optional[QWidget] = None):
        super().__init__(
            title=title,
            subtitle="Select one item to populate the editor",
            accent=accent,
            action_label=action_label,
            parent=parent,
        )
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
            "QScrollBar:vertical {"
            f"background: {DRACULA['bg0']};"
            "width: 10px;"
            "border-radius: 5px;"
            "}"
            "QScrollBar::handle:vertical {"
            f"background: {DRACULA['border']};"
            "min-height: 24px;"
            "border-radius: 5px;"
            "}"
            "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }"
        )
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 4, 0)
        self.container_layout.setSpacing(10)
        self.scroll.setWidget(self.container)
        self.set_content_widget(self.scroll)

    def set_items(self, items: List[Dict[str, str]], selected_id: str):
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        for item_data in items:
            button = ListItemButton(item_data["title"], item_data["subtitle"], self.accent)
            button.clicked.connect(lambda _checked=False, item_id=item_data["id"]: self.selection_changed.emit(item_id))
            button.setChecked(item_data["id"] == selected_id)
            self.container_layout.addWidget(button)

        self.container_layout.addStretch(1)


class MentionItemButton(QPushButton):
    def __init__(self, item: MentionItem, accent: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(76)
        self.setText(f"{item.label}\n{item.caption}")
        self.setStyleSheet(
            "QPushButton {"
            f"background: {DRACULA['bg0']};"
            f"border: 1px solid {DRACULA['border']};"
            "border-radius: 14px;"
            "padding: 12px 14px;"
            f"color: {DRACULA['fg']};"
            "text-align: left;"
            "font-size: 13px;"
            "font-weight: 600;"
            "}"
            "QPushButton:hover {"
            f"background: {DRACULA['bg3']};"
            "padding-left: 16px;"
            "}"
        )


class MentionPanel(CollapsibleCard):
    mention_requested = pyqtSignal(str)

    def __init__(self, section: MentionSection, parent: Optional[QWidget] = None):
        super().__init__(
            title=section.title,
            subtitle="Click to mention in the page",
            accent=section.accent,
            icon_text=section.icon,
            parent=parent,
        )
        self.section = section
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setMaximumHeight(220)
        self.scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
            "QScrollBar:vertical {"
            f"background: {DRACULA['bg0']};"
            "width: 10px;"
            "border-radius: 5px;"
            "}"
            "QScrollBar::handle:vertical {"
            f"background: {DRACULA['border']};"
            "min-height: 24px;"
            "border-radius: 5px;"
            "}"
            "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }"
        )
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 4, 0)
        self.container_layout.setSpacing(10)
        self.scroll.setWidget(self.container)
        self.set_content_widget(self.scroll)
        self.set_items(section.items)

    def set_items(self, items: List[MentionItem]):
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        for mention in items:
            button = MentionItemButton(mention, self.accent)
            button.clicked.connect(lambda _checked=False, token=mention.token: self.mention_requested.emit(token))
            self.container_layout.addWidget(button)

        self.container_layout.addStretch(1)


class ToolbarButton(QPushButton):
    def __init__(self, label: str, icon_text: str, parent: Optional[QWidget] = None):
        super().__init__(f"{icon_text}  {label}", parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(34)
        self.setStyleSheet(
            "QPushButton {"
            f"background: {DRACULA['bg2']};"
            f"border: 1px solid {DRACULA['border']};"
            f"color: {DRACULA['fg']};"
            "border-radius: 10px;"
            "padding: 6px 12px;"
            "font-size: 12px;"
            "font-weight: 600;"
            "}"
            "QPushButton:hover {"
            f"background: {DRACULA['bg3']};"
            "}"
        )


class LabNotebookWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.collections = build_initial_collections()
        self.mention_sections = build_initial_mentions()
        self.mode = "notebook"
        self.selected_notebook = {"notebook": "zircon-dating", "log": "daily-lab-log"}
        self.selected_page = {"notebook": "prep-notes", "log": "monday-shift"}
        self._loading_editor = False

        self.setWindowTitle("Lab knowledge workspace")
        self.resize(1450, 930)
        self.setStyleSheet(
            f"QWidget {{ background: {DRACULA['bg0']}; color: {DRACULA['fg']}; font-family: Inter, Segoe UI, Arial; }}"
        )
        self._build_ui()
        self._refresh_mode_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        page_layout = QVBoxLayout(central)
        page_layout.setContentsMargins(24, 24, 24, 24)
        page_layout.setSpacing(0)

        self.window_card = QFrame()
        self.window_card.setStyleSheet(
            "QFrame {"
            f"background: {DRACULA['bg1']};"
            f"border: 1px solid {DRACULA['border']};"
            "border-radius: 26px;"
            "}"
        )
        page_layout.addWidget(self.window_card)

        root_layout = QVBoxLayout(self.window_card)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.addWidget(self._build_header())

        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)
        body_layout.addWidget(self._build_sidebar())
        body_layout.addWidget(self._build_main_workspace(), 1)
        root_layout.addWidget(body, 1)

    def _build_header(self) -> QWidget:
        header = QFrame()
        header.setStyleSheet(
            "QFrame {"
            f"background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 {DRACULA['bg2']}, stop:1 {DRACULA['bg1']});"
            f"border-bottom: 1px solid {DRACULA['border']};"
            "border-top-left-radius: 26px;"
            "border-top-right-radius: 26px;"
            "}"
        )
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        title_stack = QVBoxLayout()
        title_stack.setContentsMargins(0, 0, 0, 0)
        title_stack.setSpacing(3)
        title = QLabel("Lab knowledge workspace")
        title.setFont(QFont("Inter", 14, QFont.Bold))
        subtitle = QLabel("Structured notes, linked entities, and quick rich-text editing")
        subtitle.setStyleSheet(f"color: {DRACULA['muted']}; font-size: 11px;")
        title_stack.addWidget(title)
        title_stack.addWidget(subtitle)
        layout.addLayout(title_stack)
        layout.addStretch(1)

        minimize_button = QPushButton("—")
        close_button = QPushButton("✕")
        for button, color in ((minimize_button, DRACULA["fg"]), (close_button, DRACULA["red"])):
            button.setFixedSize(30, 30)
            button.setCursor(Qt.PointingHandCursor)
            button.setStyleSheet(
                "QPushButton {"
                "background: transparent;"
                "border: none;"
                f"color: {color};"
                "font-size: 14px;"
                "font-weight: 700;"
                "}"
                "QPushButton:hover {"
                f"background: {DRACULA['bg3']};"
                "border-radius: 9px;"
                "}"
            )
            layout.addWidget(button)

        minimize_button.clicked.connect(self.showMinimized)
        close_button.clicked.connect(self.close)
        return header

    def _build_sidebar(self) -> QWidget:
        sidebar = QFrame()
        sidebar.setFixedWidth(210)
        sidebar.setStyleSheet(
            "QFrame {"
            f"background: {DRACULA['bg2']};"
            f"border-right: 1px solid {DRACULA['border']};"
            "border-bottom-left-radius: 26px;"
            "}"
        )
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        workspace_card = QFrame()
        workspace_card.setStyleSheet(
            "QFrame {"
            f"background: {DRACULA['bg1']};"
            f"border: 1px solid {DRACULA['border']};"
            "border-radius: 18px;"
            "}"
        )
        workspace_layout = QVBoxLayout(workspace_card)
        workspace_layout.setContentsMargins(12, 12, 12, 12)
        workspace_layout.setSpacing(10)

        workspace_label = QLabel("WORKSPACE")
        workspace_label.setStyleSheet(f"color: {DRACULA['muted']}; font-size: 10px; font-weight: 700; letter-spacing: 2px;")
        workspace_layout.addWidget(workspace_label)

        self.notebook_mode_button = SidebarModeButton("Lab Notebook", "📘")
        self.log_mode_button = SidebarModeButton("Lab Log", "🗒")
        self.notebook_mode_button.clicked.connect(lambda: self._set_mode("notebook"))
        self.log_mode_button.clicked.connect(lambda: self._set_mode("log"))
        workspace_layout.addWidget(self.notebook_mode_button)
        workspace_layout.addWidget(self.log_mode_button)
        layout.addWidget(workspace_card)

        session_card = QFrame()
        session_card.setStyleSheet(
            "QFrame {"
            f"background: {DRACULA['bg1']};"
            f"border: 1px solid {DRACULA['border']};"
            "border-radius: 18px;"
            "}"
        )
        session_layout = QVBoxLayout(session_card)
        session_layout.setContentsMargins(12, 12, 12, 12)
        session_layout.setSpacing(10)

        session_label = QLabel("SESSION")
        session_label.setStyleSheet(f"color: {DRACULA['muted']}; font-size: 10px; font-weight: 700; letter-spacing: 2px;")
        session_layout.addWidget(session_label)

        self.mode_metric = InfoMetric("Mode", "Notebook", DRACULA["pink"])
        self.notebooks_metric = InfoMetric("Notebooks", "0", DRACULA["cyan"])
        self.pages_metric = InfoMetric("Pages", "0", DRACULA["green"])
        session_layout.addWidget(self.mode_metric)
        session_layout.addWidget(self.notebooks_metric)
        session_layout.addWidget(self.pages_metric)
        layout.addWidget(session_card)
        layout.addStretch(1)
        return sidebar

    def _build_main_workspace(self) -> QWidget:
        main = QFrame()
        main.setStyleSheet(f"QFrame {{ background: {DRACULA['bg0']}; border: none; }}")
        outer = QHBoxLayout(main)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(16)

        left_column = QWidget()
        left_grid = QGridLayout(left_column)
        left_grid.setContentsMargins(0, 0, 0, 0)
        left_grid.setHorizontalSpacing(16)
        left_grid.setVerticalSpacing(16)

        self.notebooks_panel = ListPanel("Notebooks", "New", DRACULA["purple"])
        self.pages_panel = ListPanel("Pages", "Page", DRACULA["cyan"])
        self.notebooks_panel.selection_changed.connect(self._select_notebook)
        self.pages_panel.selection_changed.connect(self._select_page)
        left_grid.addWidget(self.notebooks_panel, 0, 0)
        left_grid.addWidget(self.pages_panel, 0, 1)
        left_grid.setColumnStretch(0, 1)
        left_grid.setColumnStretch(1, 1)

        editor_card = QFrame()
        editor_card.setStyleSheet(
            "QFrame {"
            f"background: {DRACULA['bg1']};"
            f"border: 1px solid {DRACULA['border']};"
            "border-radius: 24px;"
            "}"
        )
        editor_layout = QVBoxLayout(editor_card)
        editor_layout.setContentsMargins(16, 16, 16, 16)
        editor_layout.setSpacing(14)

        toolbar_row = QHBoxLayout()
        toolbar_row.setContentsMargins(0, 0, 0, 0)
        toolbar_row.setSpacing(8)

        self.bold_button = ToolbarButton("Bold", "B")
        self.italic_button = ToolbarButton("Italic", "I")
        self.underline_button = ToolbarButton("Underline", "U")
        self.mention_button = ToolbarButton("Mention", "@")
        self.bold_button.clicked.connect(lambda: self._toggle_format("bold"))
        self.italic_button.clicked.connect(lambda: self._toggle_format("italic"))
        self.underline_button.clicked.connect(lambda: self._toggle_format("underline"))

        toolbar_row.addWidget(self.bold_button)
        toolbar_row.addWidget(self.italic_button)
        toolbar_row.addWidget(self.underline_button)
        toolbar_row.addWidget(self.mention_button)
        toolbar_row.addStretch(1)

        self.page_title_input = QLineEdit()
        self.page_title_input.setReadOnly(True)
        self.page_title_input.setMinimumHeight(38)
        self.page_title_input.setMinimumWidth(260)
        self.page_title_input.setStyleSheet(
            "QLineEdit {"
            f"background: {DRACULA['bg2']};"
            f"border: 1px solid {DRACULA['border']};"
            f"color: {DRACULA['fg']};"
            "border-radius: 12px;"
            "padding: 8px 12px;"
            "font-size: 12px;"
            "font-weight: 600;"
            "}"
        )
        toolbar_row.addWidget(self.page_title_input)
        editor_layout.addLayout(toolbar_row)

        editor_shell = QFrame()
        editor_shell.setStyleSheet(
            "QFrame {"
            f"background: transparent;"
            f"border: 1px solid {DRACULA['border']};"
            "border-radius: 22px;"
            "}"
        )
        shell_layout = QVBoxLayout(editor_shell)
        shell_layout.setContentsMargins(18, 18, 18, 18)
        shell_layout.setSpacing(0)

        self.editor = QTextEdit()
        self.editor.setAcceptRichText(True)
        self.editor.setFrameShape(QFrame.NoFrame)
        self.editor.setMinimumHeight(640)
        self.editor.setStyleSheet(
            "QTextEdit {"
            f"background: {DRACULA['white_page']};"
            "border: 1px solid #E6E8F2;"
            "border-radius: 24px;"
            f"color: {DRACULA['white_ink']};"
            "padding: 18px 24px;"
            "selection-background-color: #D7DCF4;"
            "font-size: 14px;"
            "}"
        )
        self.mention_button.clicked.connect(self.editor.setFocus)
        self.editor.textChanged.connect(self._handle_editor_changed)
        shell_layout.addWidget(self.editor)
        editor_layout.addWidget(editor_shell, 1)

        outer.addWidget(left_column, 1)
        outer.addWidget(editor_card, 2)

        right_column = QWidget()
        right_layout = QVBoxLayout(right_column)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(16)
        for section in self.mention_sections:
            panel = MentionPanel(section)
            panel.mention_requested.connect(self._insert_mention)
            right_layout.addWidget(panel)
        right_layout.addStretch(1)
        outer.addWidget(right_column)

        outer.setStretch(0, 4)
        outer.setStretch(1, 5)
        outer.setStretch(2, 3)
        return main

    def _set_mode(self, mode: str):
        if self.mode == mode:
            return
        self._store_current_page_content()
        self.mode = mode
        self._refresh_mode_ui()

    def _refresh_mode_ui(self):
        self.notebook_mode_button.set_active(self.mode == "notebook")
        self.log_mode_button.set_active(self.mode == "log")

        notebooks = self.collections[self.mode]
        if not notebooks:
            return

        selected_notebook_id = self.selected_notebook.get(self.mode, notebooks[0].id)
        if not any(notebook.id == selected_notebook_id for notebook in notebooks):
            selected_notebook_id = notebooks[0].id
            self.selected_notebook[self.mode] = selected_notebook_id

        active_notebook = self._active_notebook()
        if active_notebook is None:
            return

        default_page_id = active_notebook.pages[0].id if active_notebook.pages else ""
        selected_page_id = self.selected_page.get(self.mode, default_page_id)
        if active_notebook.pages and not any(page.id == selected_page_id for page in active_notebook.pages):
            selected_page_id = default_page_id
            self.selected_page[self.mode] = selected_page_id

        self.notebooks_panel.set_title("Notebooks" if self.mode == "notebook" else "Logs")
        self.mode_metric.set_value("Notebook" if self.mode == "notebook" else "Log")
        self.notebooks_metric.set_value(str(len(notebooks)))
        self.pages_metric.set_value(str(len(active_notebook.pages)))

        self.notebooks_panel.set_items(
            [{"id": notebook.id, "title": notebook.title, "subtitle": notebook.subtitle} for notebook in notebooks],
            self.selected_notebook[self.mode],
        )
        self.pages_panel.set_items(
            [{"id": page.id, "title": page.title, "subtitle": page.summary} for page in active_notebook.pages],
            self.selected_page[self.mode],
        )

        active_page = self._active_page()
        self.page_title_input.setText(active_page.title if active_page else "")
        self._load_active_page_into_editor()

    def _active_notebook(self) -> Optional[NotebookRecord]:
        notebooks = self.collections[self.mode]
        if not notebooks:
            return None
        return next(
            (notebook for notebook in notebooks if notebook.id == self.selected_notebook.get(self.mode)),
            notebooks[0],
        )

    def _active_page(self) -> Optional[NotebookPage]:
        notebook = self._active_notebook()
        if notebook is None or not notebook.pages:
            return None
        return next(
            (page for page in notebook.pages if page.id == self.selected_page.get(self.mode)),
            notebook.pages[0],
        )

    def _select_notebook(self, notebook_id: str):
        self._store_current_page_content()
        self.selected_notebook[self.mode] = notebook_id
        notebook = self._active_notebook()
        if notebook and notebook.pages:
            self.selected_page[self.mode] = notebook.pages[0].id
        self._refresh_mode_ui()

    def _select_page(self, page_id: str):
        self._store_current_page_content()
        self.selected_page[self.mode] = page_id
        self._refresh_mode_ui()

    def _load_active_page_into_editor(self):
        page = self._active_page()
        self._loading_editor = True
        self.editor.setHtml(page.content if page else "")
        self._loading_editor = False

    def _store_current_page_content(self):
        if self._loading_editor:
            return
        page = self._active_page()
        if page is not None:
            page.content = self.editor.toHtml()

    def _handle_editor_changed(self):
        if self._loading_editor:
            return
        page = self._active_page()
        if page is not None:
            page.content = self.editor.toHtml()

    def _toggle_format(self, kind: str):
        self.editor.setFocus()
        cursor = self.editor.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)
            self.editor.setTextCursor(cursor)

        current_format = cursor.charFormat()
        new_format = QTextCharFormat()
        if kind == "bold":
            new_format.setFontWeight(QFont.Normal if current_format.fontWeight() == QFont.Bold else QFont.Bold)
        elif kind == "italic":
            new_format.setFontItalic(not current_format.fontItalic())
        elif kind == "underline":
            new_format.setFontUnderline(not current_format.fontUnderline())

        cursor.mergeCharFormat(new_format)
        self.editor.mergeCurrentCharFormat(new_format)

    def _insert_mention(self, token: str):
        self.editor.setFocus()
        cursor = self.editor.textCursor()
        mention_format = QTextCharFormat()
        mention_format.setForeground(QColor(DRACULA["purple"]))
        mention_format.setFontWeight(QFont.Bold)
        cursor.insertText(f"{token} ", mention_format)
        self.editor.setTextCursor(cursor)
        self._handle_editor_changed()


def run_preview():
    app = QApplication.instance()
    created_app = False
    if app is None:
        app = QApplication([])
        created_app = True

    window = LabNotebookWindow()
    window.show()

    if created_app:
        app.exec_()


if __name__ == "__main__":
    run_preview()

from dataclasses import dataclass
from typing import List, Optional, Dict
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QPushButton, QWidget, QSizePolicy)


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


class MentionItemButton(QPushButton):
    def __init__(self, item: MentionItem, accent: str,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.setCursor(Qt.PointingHandCursor)

        self.setText(f"{item.label}\n{item.caption}")

        fm = self.fontMetrics()

        height = (
            fm.lineSpacing() * 2
            + 24  # padding compensation
        )

        self.setMinimumHeight(height)

        self.setStyleSheet(
            f"""
            QPushButton {{
                background: {DRACULA['bg0']};
                border: 1px solid {DRACULA['border']};
                border-radius: 10px;
                padding: 10px 10px;
                color: {accent};
                text-align: left;
                font-size: 8pt;
            }}

            QPushButton:hover {{
                background: {DRACULA['bg3']};
                padding-left: 12px;
            }}
            """
        )
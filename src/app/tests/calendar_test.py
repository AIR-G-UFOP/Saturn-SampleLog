from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys


class DayWidget(QFrame):
    def __init__(self, date):
        super().__init__()
        self.date = date

        self.setMinimumHeight(80)
        self.setStyleSheet("background:#12162a;border:1px solid #2a2f45;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        label = QLabel(str(date.day()))
        label.setStyleSheet("color:white;")
        layout.addWidget(label, alignment=Qt.AlignTop | Qt.AlignLeft)


class CalendarWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Calendar")
        self.resize(900, 600)

        self.current = QDate.currentDate()
        self.events = []
        self.day_widgets = {}

        main = QVBoxLayout(self)

        # Header
        header = QHBoxLayout()
        self.prev = QPushButton("<")
        self.next = QPushButton(">")
        self.title = QLabel()
        self.title.setAlignment(Qt.AlignCenter)

        header.addWidget(self.prev)
        header.addWidget(self.title)
        header.addWidget(self.next)

        main.addLayout(header)

        # Grid
        self.grid = QGridLayout()
        self.grid.setSpacing(4)
        main.addLayout(self.grid)

        # Overlay INSIDE same parent as grid
        self.overlay = QWidget(self)
        self.overlay.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.overlay.raise_()

        self.prev.clicked.connect(self.prev_month)
        self.next.clicked.connect(self.next_month)

        self.refresh()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.overlay.setGeometry(self.rect())

    def add_event(self, start, end, title, color="#5c6bc0"):
        self.events.append({
            "start": start,
            "end": end,
            "title": title,
            "color": color
        })
        self.refresh()

    def refresh(self):
        # clear grid
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.day_widgets.clear()

        year = self.current.year()
        month = self.current.month()

        self.title.setText(f"{month}/{year}")

        first = QDate(year, month, 1)
        start_col = first.dayOfWeek() - 1
        days = first.daysInMonth()

        row = 0
        col = start_col

        for d in range(1, days + 1):
            date = QDate(year, month, d)
            w = DayWidget(date)

            self.grid.addWidget(w, row, col)
            self.day_widgets[date] = w

            col += 1
            if col > 6:
                col = 0
                row += 1

        # IMPORTANT: delay drawing until layout is ready
        QTimer.singleShot(0, self.draw_events)

    def draw_events(self):
        # clear overlay
        for c in self.overlay.children():
            c.deleteLater()

        self.overlay.setGeometry(self.rect())

        for ev in self.events:
            start = ev["start"]
            end = ev["end"]

            current = start

            while current <= end:
                week_start = current

                # go to end of week
                while current <= end and current.dayOfWeek() != 7:
                    current = current.addDays(1)

                week_end = min(current, end)

                if week_start not in self.day_widgets or week_end not in self.day_widgets:
                    current = current.addDays(1)
                    continue

                w1 = self.day_widgets[week_start]
                w2 = self.day_widgets[week_end]

                # map into overlay coordinates
                p1 = w1.mapTo(self.overlay, QPoint(0, 0))
                p2 = w2.mapTo(self.overlay, QPoint(w2.width(), 0))

                bar = QLabel(ev["title"], self.overlay)

                bar.setStyleSheet(f"""
                    background:{ev['color']};
                    color:white;
                    border-radius:6px;
                    padding-left:4px;
                """)

                bar.setGeometry(
                    p1.x() + 2,
                    p1.y() + 20,
                    p2.x() - p1.x() - 4,
                    18
                )

                bar.show()

                current = current.addDays(1)

    def prev_month(self):
        self.current = self.current.addMonths(-1)
        self.refresh()

    def next_month(self):
        self.current = self.current.addMonths(1)
        self.refresh()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    w = CalendarWidget()

    today = QDate.currentDate()
    w.add_event(today, today.addDays(3), "Campaign")
    w.add_event(today.addDays(2), today.addDays(6), "Overlap")

    w.show()
    sys.exit(app.exec_())
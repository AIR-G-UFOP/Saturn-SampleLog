from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "data"

DATABASE_URL = f"sqlite:///{DATA_DIR / 'database.db'}"
ENABLE_CUSTOM_TITLE_BAR = True
DEFAULT_MENU_WIDTH = 50
MENU_WIDTH = 200
TIME_ANIMATION = 500
MENU_SELECTED_STYLESHEET = """
border-left: 17px solid qlineargradient(spread:pad, x1:0.034, y1:0, x2:0.216, y2:0, stop:0.499 #FF5555, stop:0.5 rgba(85, 170, 255, 0));
background-color: rgb(33, 37, 43);
"""
CARD_MIN_HEIGHT = 50
CARD_HOVER_STYLESHEET = """
#bgCard {
background-color: #343746;
}
"""
CARD_NORMAL_STYLESHEET = """
#bgCard {
background-color: #282A36;
}
"""
CARD_SUBHEADING_TEXT_COLOUR = "color: #F8F8F2"
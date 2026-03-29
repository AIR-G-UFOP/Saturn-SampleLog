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
CARD_BUTTON_ICON_UP = u":/icons/icons/cil-arrow-up.png"
CARD_BUTTON_ICON_DOWN = u":/icons/icons/cil-arrow-down.png"
CARD_MIN_HEIGHT = 159
WIDGET_INFO_HEIGHT = 86
USER_DETAILS_HEIGHT = 54
SAMPLE_DETAILS_HEIGHT = 74
ANALYSIS_DETAILS_HEIGHT = 94
WIDGET_INFO_STYLESHEET = ("""QFrame[role='card'] {
                          background-color: #343746;
                          border-radius: 10px;
                          border: 1px solid #525f7f;
                          }""")
CARD_SUBHEADING_STYLESHEET = "font: 10pt; color: #F8F8F2"
LABEL_COLOUR = "color: #BDBDBD"
SAMPLE_STATUS_COLOUR = {
    "Logged in": "#BDBDBD",
    "Preparation in progress...": "color: #F1FA8C",
    "Preparation completed": "color: #50FA7B",
    "Analysis in progress...": "color: #F1FA8C",
    "Analysis completed": "color: #50FA7B",
    "Data Reduction in progress...": "color: #F1FA8C",
    "Data reduction completed": "color: #50FA7B",
    "Sent back to User": "color: #BDBDBD",
}
ANALYSIS_STATUS_COLOUR = {
    "Logged in": "#BDBDBD",
    "Analysis in progress...": "color: #F1FA8C",
    "Analysis completed": "color: #50FA7B",
    "Data reduction in progress...": "color: #F1FA8C",
    "Data reduction completed": "color: #50FA7B",
    "Results sent to User": "color: #BDBDBD",
}
REDUCTION_STATUS_COLOUR = {
    "Logged in": "color: #BDBDBD",
    "Data Reduction in progress...": "color: #F1FA8C",
    "Data reduction completed": "color: #50FA7B",
    "Results sent to User": "color: #BDBDBD",
}
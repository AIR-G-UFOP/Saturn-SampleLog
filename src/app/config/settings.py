from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "data"

DATABASE_URL = f"sqlite:///{DATA_DIR / 'database.db'}"
ENABLE_CUSTOM_TITLE_BAR = True

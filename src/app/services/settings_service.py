import sys
from sqlalchemy.exc import SQLAlchemyError
from ..db.session import SessionLocal
from ..db.models import DbSettings


class SettingsService:
    def __init__(self):
        self.DEFAULT_FILE_NAME_SETTINGS = {
            "template": ['Current date', 'Analysis/Reduction name'],
            "separator": "_"
        }

    def getFileNameSettings(self):
        session = SessionLocal()
        try:
            settings = session.query(DbSettings).first()
            if not settings:
                return self.DEFAULT_FILE_NAME_SETTINGS
            return settings.file_name_config
        finally:
            session.close()

    def saveFileNameSettings(self, file_name_config):
        session = SessionLocal()
        try:
            settings = session.query(DbSettings).first()
            if not settings:
                settings = DbSettings(file_name_config=file_name_config)
                session.add(settings)
            else:
                settings.file_name_config = file_name_config
            session.commit()
            return "Settings saved successfully."
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error saving settings: {str(e)}", file=sys.stderr)
            return f"Error saving settings. Please try again."
        finally:
            session.close()

    def initSettings(self):
        session = SessionLocal()
        try:
            settings = session.query(DbSettings).first()
            if not settings:
                settings = DbSettings(file_name_config=self.DEFAULT_FILE_NAME_SETTINGS)
                session.add(settings)
                session.commit()
                print("Default settings created.")
        except Exception as e:
            session.rollback()
            print(f"Error initializing settings: {e}")
        finally:
            session.close()

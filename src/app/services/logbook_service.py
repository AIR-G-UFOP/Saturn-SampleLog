import sys

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from ..db.session import SessionLocal
from ..db.models import DbLogbook, DbLogbookTable


class LogbookService:

    def addLogbook(self, logbook_info):
        session = SessionLocal()
        try:
            new_logbook = DbLogbook(
                title=logbook_info["title"],
                description=logbook_info["description"],
                created_at=logbook_info["created_at"],
                modified_at=logbook_info["modified_at"],
                order=logbook_info["order"]
            )
            session.add(new_logbook)
            session.commit()
            return "Logbook added successfully."
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error adding Logbook: {e}", file=sys.stderr)
            return "Error adding Logbook. Please try again."
        finally:
            session.close()

    def editLogbook(self, logbook_info, logbook_id):
        session = SessionLocal()
        try:
            logbook = session.get(DbLogbook, logbook_id)
            logbook.title = logbook_info["title"]
            logbook.description = logbook_info["description"]
            logbook.modified_at = logbook_info["modified_at"]
            logbook.order = logbook_info["order"]
            session.commit()
            return "Logbook edited successfully."
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error editing Logbook: {e}", file=sys.stderr)
            return "Error editing Logbook. Please try again."
        finally:
            session.close()

    def deleteLogbook(self, logbook_id):
        session = SessionLocal()
        try:
            logbook = session.get(DbLogbook, logbook_id)
            session.delete(logbook)
            session.commit()
            return "Logbook deleted successfully."
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error deleting Logbook: {e}", file=sys.stderr)
            return "Error deleting Logbook. Please try again."
        finally:
            session.close()

    def getAllLogbooks(self):
        session = SessionLocal()
        try:
            all_logbooks = session.querry(DbLogbook).all()
            return all_logbooks
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error getting Logbooks: {e}", file=sys.stderr)
            return []
        finally:
            session.close()

    def getAllLogbooksFull(self):
        session = SessionLocal()
        try:
            logbooks = (
                session.query(DbLogbook)
                .options(
                    selectinload(DbLogbook.tables)
                )
                .all()
            )
            return logbooks
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error getting Logbooks: {e}", file=sys.stderr)
            return []
        finally:
            session.close()

    def addTable(self, table_info):
        session = SessionLocal()
        try:
            new_table = DbLogbookTable(
                title=table_info["title"],
                description=table_info["description"],
                created_at=table_info["created_at"],
                modified_at=table_info["modified_at"],
                table_order=table_info["table_order"],
                content=table_info["content"],
                logbook_id=table_info["logbook_id"]
            )
            session.add(new_table)
            session.commit()
            return "Table added successfully."
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error adding Table: {e}", file=sys.stderr)
            return "Error adding Table. Please try again."
        finally:
            session.close()

    def editTable(self, table_info, table_id):
        session = SessionLocal()
        try:
            table = session.get(DbLogbookTable, table_id)
            table.title = table_info["title"]
            table.description = table_info["description"]
            table.modified_at = table_info["modified_at"]
            table.table_order = table_info["table_order"]
            table.content = table_info["content"]
            session.commit()
            return "Table edited successfully."
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error editing Table: {e}", file=sys.stderr)
            return "Error editing Table. Please try again."
        finally:
            session.close()

    def deleteTable(self, table_id):
        session = SessionLocal()
        try:
            table = session.get(DbLogbookTable, table_id)
            session.delete(table)
            session.commit()
            return "Table deleted successfully."
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error deleting Table: {e}", file=sys.stderr)
            return "Error deleting Table. Please try again."
        finally:
            session.close()

    def getAllTables(self):
        session = SessionLocal()
        try:
            all_tables = session.query(DbLogbookTable).all()
            return all_tables
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error getting Tables: {e}", file=sys.stderr)
            return []
        finally:
            session.close()
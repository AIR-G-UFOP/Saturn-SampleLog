import sys

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from ..db.session import SessionLocal
from ..db.models import DbNotebookSession, DbNotebook


class NotebookService:

    def addNotebook(self, notebook_info):
        session = SessionLocal()
        try:
            new_notebook = DbNotebook(
                title=notebook_info["title"],
                description=notebook_info["description"],
                created_at=notebook_info["created_at"],
                modified_at=notebook_info["modified_at"],
                order=notebook_info["order"]
            )
            session.add(new_notebook)
            session.commit()
            return "Notebook added successfully."
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error adding Notebook: {e}", file=sys.stderr)
            return "Error adding Notebook. Please try again."
        finally:
            session.close()

    def editNotebook(self, notebook_info, notebook_id):
        session = SessionLocal()
        try:
            notebook = session.get(DbNotebook, notebook_id)
            notebook.title = notebook_info["title"]
            notebook.description = notebook_info["description"]
            notebook.modified_at = notebook_info["modified_at"]
            notebook.order = notebook_info["order"]
            session.commit()
            return "Notebook edited successfully."
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error editing Notebook: {e}", file=sys.stderr)
            return "Error editing Notebook. Please try again."
        finally:
            session.close()

    def deleteNotebook(self, notebook_id):
        session = SessionLocal()
        try:
            notebook = session.get(DbNotebook, notebook_id)
            session.delete(notebook)
            session.commit()
            return "Notebook deleted successfully."
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error deleting Notebook: {e}", file=sys.stderr)
            return "Error deleting Notebook. Please try again."
        finally:
            session.close()

    def getAllNotebooks(self):
        session = SessionLocal()
        try:
            notebooks = session.querry(DbNotebook).all()
            return notebooks
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error getting Notebooks: {e}", file=sys.stderr)
            return []
        finally:
            session.close()

    def getAllNotebooksFull(self):
        session = SessionLocal()
        try:
            notebooks = (
                session.query(DbNotebook)
                .options(
                    selectinload(DbNotebook.sessions)
                )
                .all()
            )
            return notebooks
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error getting Notebooks: {e}", file=sys.stderr)
            return []
        finally:
            session.close()

    def addSession(self, session_info):
        session = SessionLocal()
        try:
            new_session = DbNotebookSession(
                title=session_info["title"],
                description=session_info["description"],
                created_at=session_info["created_at"],
                modified_at=session_info["modified_at"],
                session_order=session_info["order"],
                notebook_id=session_info["notebook_id"],
                content=session_info["content"]
            )
            session.add(new_session)
            session.commit()
            return "Session added successfully."
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error adding Session: {e}", file=sys.stderr)
            return "Error adding Session. Please try again."
        finally:
            session.close()

    def editSession(self, session_info, session_id):
        session = SessionLocal()
        try:
            notebook_session = session.get(DbNotebook, session_id)
            notebook_session.title = session_info["title"]
            notebook_session.description = session_info["description"]
            notebook_session.modified_at = session_info["modified_at"]
            notebook_session.session_order = session_info["order"]
            notebook_session.content = session_info["content"]
            session.commit()
            return "Session edited successfully."
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error editing Session: {e}", file=sys.stderr)
            return "Error editing Session. Please try again."
        finally:
            session.close()

    def deleteSession(self, session_id):
        session = SessionLocal()
        try:
            notebook_session = session.get(DbNotebook, session_id)
            session.delete(notebook_session)
            session.commit()
            return "Session deleted successfully."
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error deleting Session: {e}", file=sys.stderr)
            return "Error deleting Session. Please try again."
        finally:
            session.close()

    def getAllSessions(self):
        session = SessionLocal()
        try:
            notebooks = session.query(DbNotebook).all()
            return notebooks
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error getting Sessions: {e}", file=sys.stderr)
            return []
        finally:
            session.close()

    def getSessionById(self, session_id):
        session = SessionLocal()
        try:
            notebook_session = session.get(DbNotebookSession, session_id)
            return notebook_session
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error getting Session: {e}", file=sys.stderr)
            return None
        finally:
            session.close()





import sys
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from ..db.models import DBTasks
from ..db.session import SessionLocal


class TaskService:

    def addTask(self, task_info):
        session = SessionLocal()
        try:
            new_task = DBTasks(
                name=task_info["name"],
                description=task_info["description"],
                start_date=task_info["start_date"],
                end_date=task_info["end_date"],
                status=task_info["status"],
                task_type=task_info["task_type"],
                sample_id=task_info.get("sample_id")
            )
            session.add(new_task)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error adding Task: {str(e)}", file=sys.stderr)
        finally:
            session.close()
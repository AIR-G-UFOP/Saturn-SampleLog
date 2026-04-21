import sys
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import selectinload
from ..db.models import DBTasks
from ..db.session import SessionLocal


class TaskService:

    def addTask(self, task_info):
        session = SessionLocal()
        try:
            task = DBTasks(**task_info)
            session.add(task)
            session.commit()
            return task

        except IntegrityError:
            session.rollback()
            raise ValueError("Task already exists with same type, name and dates")

        finally:
            session.close()
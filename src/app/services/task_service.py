import sys
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import selectinload
from ..db.models import DBTasks
from ..db.session import SessionLocal


class TaskService:

    def upsertTask(self, task_info):
        session = SessionLocal()
        try:
            existing = self.get_task(
                task_type=task_info["task_type"],
                sample_id=task_info.get("sample_id"),
                analysis_id=task_info.get("analysis_id"),
                reduction_id=task_info.get("reduction_id"),
            )

            if existing:
                existing.description = task_info["description"]
                existing.status = task_info["status"]
                existing.start_date = task_info["start_date"]
                existing.end_date = task_info["end_date"]
                session.commit()
                print("updated")

            else:
                new_task = DBTasks(**task_info)
                session.add(new_task)
                session.commit()
                print("created")

        finally:
            session.close()

    @staticmethod
    def get_task(task_type, sample_id=None, analysis_id=None, reduction_id=None):
        session = SessionLocal()
        try:
            query = session.query(DBTasks).filter(DBTasks.task_type == task_type)

            if sample_id:
                query = query.filter(DBTasks.sample_id == sample_id)
            elif analysis_id:
                query = query.filter(DBTasks.analysis_id == analysis_id)
            elif reduction_id:
                query = query.filter(DBTasks.reduction_id == reduction_id)

            return query.first()

        finally:
            session.close()

    def getTasksByDate(self, date):
        session = SessionLocal()
        try:
            query = session.query(DBTasks).filter(DBTasks.start_date == date).all()
            return query
        finally:
            session.close()

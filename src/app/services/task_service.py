import sys
from datetime import date
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import selectinload
from ..db.models import DbTasks
from ..db.session import SessionLocal


class TaskService:

    def upsertTask(self, task_info):
        session = SessionLocal()

        try:
            task_id = task_info.get("id")
            task_type = task_info["task_type"]
            if task_id:
                task = session.get(DbTasks, task_id)
                if not task:
                    print("Task not found")
                    return
                task.name = task_info["name"]
                task.description = task_info["description"]
                task.status = task_info["status"]
                task.start_date = task_info["start_date"]
                task.end_date = task_info["end_date"]
                try:
                    task.completed_at = task_info["completed_at"]
                except KeyError:
                    pass
                session.commit()
                print("updated by id")
                return

            if task_type in ["sample_preparation", "analysis", "reduction"]:
                existing = self.get_task(
                    session,
                    task_type=task_type,
                    sample_id=task_info.get("sample_id"),
                    analysis_id=task_info.get("analysis_id"),
                    reduction_id=task_info.get("reduction_id"),
                )
                if existing:
                    existing.name = task_info["name"]
                    existing.description = task_info["description"]
                    existing.status = task_info["status"]
                    existing.start_date = task_info["start_date"]
                    existing.end_date = task_info["end_date"]
                    session.commit()
                    print("updated by relation")
                    return

            new_task = DbTasks(**task_info)
            session.add(new_task)
            session.commit()
            print("created")

        finally:
            session.close()

    def deleteTask(self, task_id):
        session = SessionLocal()
        try:
            task = session.get(DbTasks, task_id)
            if not task:
                print("Task not found")
                return
            session.delete(task)
            session.commit()
            print("deleted")
            return
        except Exception as e:
            session.rollback()
            print(e)
            return
        finally:
            session.close()

    @staticmethod
    def get_task(session, task_type, sample_id=None, analysis_id=None, reduction_id=None):
        query = session.query(DbTasks).filter(DbTasks.task_type == task_type)
        if sample_id:
            query = query.filter(DbTasks.sample_id == sample_id)
        elif analysis_id:
            query = query.filter(DbTasks.analysis_id == analysis_id)
        elif reduction_id:
            query = query.filter(DbTasks.reduction_id == reduction_id)
        return query.first()

    def getTasksByDate(self, date):
        session = SessionLocal()
        try:
            query = session.query(DbTasks).filter(DbTasks.start_date == date).all()
            return query
        finally:
            session.close()

    def getTasksByMonth(self, month, year):
        session = SessionLocal()
        try:
            start = date(year, month, 1)
            if month == 12:
                end = date(year + 1, 1, 1)
            else:
                end = date(year, month + 1, 1)
            tasks = session.query(DbTasks).filter(
                DbTasks.start_date < end,
                DbTasks.end_date >= start
            ).all()
            return tasks
        finally:
            session.close()

    def getTaskById(self, task_id):
        session = SessionLocal()
        try:
            task = session.query(DbTasks).filter(DbTasks.id == task_id).first()
            return task
        finally:
            session.close()

    def getAllTasks(self):
        session = SessionLocal()
        try:
            tasks = session.query(DbTasks).all()
            return tasks
        finally:
            session.close()

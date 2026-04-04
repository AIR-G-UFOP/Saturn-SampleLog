import sys
import os
from datetime import date
from ..services.user_service import UserService
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from ..db.models import DbSample, DbAnalysis
from ..db.session import SessionLocal


class SampleService:

    def addSample(self, sample_info):
        session = SessionLocal()
        try:
            new_sample = DbSample(
                name=sample_info["name"],
                description=sample_info["description"],
                user_id=sample_info["user_id"],
                status_date=sample_info["status_date"],
                start_date=sample_info["start_date"],
                end_date=sample_info["end_date"],
                preparation=sample_info["preparation"],
                comment=sample_info["comment"],
                status=sample_info["status"])
            session.add(new_sample)
            session.commit()
            return "Sample added successfully."
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error adding Sample: {str(e)}", file=sys.stderr)
            return "Error adding Sample. Please try again."
        finally:
            session.close()

    def deleteSample(self, key):
        # test key
        # delete sample
        pass

    def editSample(self, sample_id, sample_info):
        session = SessionLocal()
        try:
            sample = session.get(DbSample, sample_id)
            sample.name = sample_info["name"]
            sample.description = sample_info["description"]
            sample.preparation = sample_info["preparation"]
            sample.comment = sample_info["comment"]
            sample.status = sample_info["status"]
            sample.status_date = sample_info["status_date"]
            sample.start_date = sample_info["start_date"]
            sample.end_date = sample_info["end_date"]
            sample.user_id = sample_info["user_id"]
            session.commit()
            return "Sample updated successfully."
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error updating Sample: {str(e)}", file=sys.stderr)
            return "Error updating Sample. Please try again."
        finally:
            session.close()

    def getAllSamples(self):
        session = SessionLocal()
        try:
            samples = session.query(DbSample).all()
            return samples
        except SQLAlchemyError as e:
            print(f"Error retrieving samples: {str(e)}", file=sys.stderr)
            return []
        finally:
            session.close()

    def getAllSamplesFull(self):
        session = SessionLocal()
        try:
            samples = (
                session.query(DbSample)
                .options(
                    selectinload(DbSample.users),
                    selectinload(DbSample.analyses)
                    .selectinload(DbAnalysis.reduction)
                )
                .all()
            )
            return samples
        finally:
            session.close()

    def findSampleById(self, sample_id):
        session = SessionLocal()
        try:
            sample = session.get(DbSample, sample_id)
            return sample
        finally:
            session.close()
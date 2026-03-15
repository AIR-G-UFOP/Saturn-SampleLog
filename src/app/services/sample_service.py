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
                date=sample_info["date"],
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

    def editSample(self, key, name, descript, status, add_date, prep, prep_comment, user):
        # test key
        if isinstance(user, UserService):
            self.name = name
            self.description = descript
            self.status = status
            self.date = add_date
            self.preparation = prep
            self.preparation_comment = prep_comment
            # user here
            # save sample to database using key
        else:
            raise Exception('Sample should have an User')
            # call an "add user?"
        # Edit sample

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
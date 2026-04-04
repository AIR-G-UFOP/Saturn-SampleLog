import sys

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from ..db.session import SessionLocal
from ..db.models import DbAnalysis, DbSample


class AnalysisService:

    def addAnalysis(self, analysis_info, sample_ids):
        session = SessionLocal()
        try:
            new_analysis = DbAnalysis(
                method=analysis_info["method"],
                equipment=analysis_info["equipment"],
                conditions=analysis_info["conditions"],
                operator=analysis_info["operator"],
                status_date=analysis_info["status_date"],
                start_date=analysis_info["start_date"],
                end_date=analysis_info["end_date"],
                file_name=analysis_info["file_name"],
                status=analysis_info["status"]
            )
            samples = session.query(DbSample).filter(DbSample.id.in_(sample_ids)).all()
            new_analysis.samples.extend(samples)
            session.add(new_analysis)
            session.commit()
            return "Analysis added successfully."
        except Exception as e:
            session.rollback()
            print(f"Error adding Analysis: {str(e)}", file=sys.stderr)
            return f"Error adding Analysis. Please try again."
        finally:
            session.close()

    def deleteAnalysis(self):
        # check key
        # delete analysis
        pass

    def editAnalysis(self, analysis_id, analysis_info, sample_ids):
        session = SessionLocal()
        try:
            analysis = session.get(DbAnalysis, analysis_id)
            analysis.method = analysis_info["method"]
            analysis.equipment = analysis_info["equipment"]
            analysis.conditions = analysis_info["conditions"]
            analysis.operator = analysis_info["operator"]
            analysis.status_date = analysis_info["status_date"]
            analysis.start_date = analysis_info["start_date"]
            analysis.end_date = analysis_info["end_date"]
            analysis.file_name = analysis_info["file_name"]
            analysis.status = analysis_info["status"]
            samples = session.query(DbSample).filter(DbSample.id.in_(sample_ids)).all()
            analysis.samples = samples
            session.commit()
            return "Analysis updated successfully."
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error updating Analysis: {str(e)}", file=sys.stderr)
            return f"Error updating Analysis. Please try again."
        finally:
            session.close()

    def getAllAnalyses(self):
        session = SessionLocal()
        try:
            analyses = session.query(DbAnalysis).all()
            return analyses
        except Exception as e:
            print(f"Error retrieving Analyses: {str(e)}", file=sys.stderr)
            return []
        finally:
            session.close()

    def getAllAnalysesFull(self):
        session = SessionLocal()
        try:
            analyses = (
                session.query(DbAnalysis)
                .options(
                    selectinload(DbAnalysis.samples)
                    .selectinload(DbSample.users),
                    selectinload(DbAnalysis.reduction)
                )
                .all()
            )
            return analyses
        finally:
            session.close()

    def findAnalysisById(self, analysis_id):
        session = SessionLocal()
        try:
            analyses = (
                session.query(DbAnalysis)
                .options(
                    selectinload(DbAnalysis.samples)
                )
                .filter(DbAnalysis.id == analysis_id)
                .first()
            )
            return analyses
        finally:
            session.close()
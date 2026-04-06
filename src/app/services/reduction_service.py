import sys

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from ..db.session import SessionLocal
from ..db.models import DbReduction, DbAnalysis, DbSample


class ReductionService:

    def addReduction(self, reduction_info):
        session = SessionLocal()
        try:
            reduction = DbReduction(
                reduction_name=reduction_info['reduction_name'],
                software=reduction_info['software'],
                software_version=reduction_info['version'],
                handler=reduction_info['handler'],
                status_date=reduction_info['status_date'],
                start_date=reduction_info['start_date'],
                end_date=reduction_info['end_date'],
                notes=reduction_info['notes'],
                file_name=reduction_info['file_name'],
                analysis_id=reduction_info['analysis_id'],
                status=reduction_info['status'],
                generate_file_name=reduction_info['generate_file_name'],
            )
            session.add(reduction)
            session.commit()
            return "Reduction logged successfully."
        except Exception as e:
            session.rollback()
            print(f"Error logging reduction: {str(e)}", file=sys.stderr)
            return "Error logging reduction. Please try again."
        finally:
            session.close()

    def editReduction(self, reduction_id, reduction_info):
        session = SessionLocal()
        try:
            reduction = session.get(DbReduction, reduction_id)
            reduction.reduction_name = reduction_info['reduction_name']
            reduction.software = reduction_info['software']
            reduction.software_version = reduction_info['version']
            reduction.handler = reduction_info['handler']
            reduction.status_date = reduction_info['status_date']
            reduction.start_date = reduction_info['start_date']
            reduction.end_date = reduction_info['end_date']
            reduction.notes = reduction_info['notes']
            reduction.file_name = reduction_info['file_name']
            reduction.analysis_id = reduction_info['analysis_id']
            reduction.status = reduction_info['status']
            reduction.generate_file_name = reduction_info['generate_file_name']
            session.commit()
            return "Reduction updated successfully."
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error updating reduction: {str(e)}", file=sys.stderr)
            return "Error updating reduction. Please try again."
        finally:
            session.close()

    def removeReduction(self):
        pass

    def getAllReductions(self):
        session = SessionLocal()
        try:
            reductions = session.query(DbReduction).all()
            return reductions
        except Exception as e:
            print(f"Error retrieving reductions: {str(e)}", file=sys.stderr)
            return []
        finally:
            session.close()

    def getAllReductionsFull(self):
        session = SessionLocal()
        try:
            reductions = (
                session.query(DbReduction)
                .options(
                    selectinload(DbReduction.analysis)
                    .selectinload(DbAnalysis.samples)
                    .selectinload(DbSample.users)
                )
                .all()
            )
            return reductions
        finally:
            session.close()

    def getReductionById(self, reduction_id):
        session = SessionLocal()
        try:
            reduction = session.get(DbReduction, reduction_id)
            return reduction
        finally:
            session.close()
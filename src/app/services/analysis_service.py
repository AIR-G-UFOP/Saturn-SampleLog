import sys
import os
from datetime import date
from ..services.sample_service import SampleService
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
                date=analysis_info["date"],
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

    def editAnalysis(self):
        pass

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
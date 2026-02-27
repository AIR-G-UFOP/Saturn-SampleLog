import sys
import os
from datetime import date
from ..services.analysis_service import AnalysisService
from ..db.session import SessionLocal
from ..db.models import DbReduction


class ReductionService:

    def addReduction(self, reduction_info):
        session = SessionLocal()
        try:
            reduction = DbReduction(
                reduction_name=reduction_info['reduction_name'],
                software=reduction_info['software'],
                software_version=reduction_info['version'],
                handler=reduction_info['handler'],
                date=reduction_info['date'],
                notes=reduction_info['notes'],
                file_id=reduction_info['file_id'],
                analysis_id=reduction_info['analysis_id']
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

    def editReduction(self):
        pass

    def removeReduction(self):
        pass
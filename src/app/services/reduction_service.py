import sys
import os
from datetime import date
from ..services.analysis_service import AnalysisService


class ReductionService:
    def __init__(self):
        self.software = str
        self.software_version = str
        self.handler = str
        self.date = date
        self.notes = str
        self.file_id = str

    def addReduction(self, software, version, handler, red_date, notes, file_id, analysis):
        if isinstance(analysis, AnalysisService):
            self.software = software
            self.software_version = version
            self.handler = handler
            self.date = red_date
            self.notes = notes
            self.file_id = file_id
            # analysis here
            # unique key
            # save
        else:
            raise Exception('Invalid analysis...')

    def deleteReduction(self, key):
        # test key
        # delete
        pass

    def editReduction(self, key, software, version, handler, red_date, notes, file_id, analysis):
        # test key
        if isinstance(analysis, AnalysisService):
            self.software = software
            self.software_version = version
            self.handler = handler
            self.date = red_date
            self.notes = notes
            self.file_id = file_id
            # analysis here
            # edit
        else:
            raise Exception('Invalid analysis...')
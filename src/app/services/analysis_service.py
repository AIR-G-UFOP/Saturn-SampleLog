import sys
import os
from datetime import date
from sample_service import Sample


class Analysis:
    def __init__(self):
        self.method = str
        self.equipment = str
        self.conditions = str
        self.operator = str
        self.date = date
        self.status = str
        self.file_id = str
        self.samples = []

    def addAnalysis(self, method, equip, conditions, operator, anal_date, status, file_id, samples):
        self.method = method
        self.equipment = equip
        self.conditions = conditions
        self.operator = operator
        self.date = anal_date
        self.status = status
        self.file_id = file_id
        if isinstance(samples, Sample):
            self.samples.append(samples)
        elif isinstance(samples, list):
            for entry in samples:
                if not isinstance(entry, Sample):
                    raise Exception(f'Invalid sample: {entry}')
                    # Add "add sample?"
            self.samples = samples
        else:
            raise Exception('Invalid sample...')
            # Add "add sample?"

    def deleteAnalysis(self, key):
        # check key
        # delete analysis
        pass

    def editAnalysis(self, key, method, equip, conditions, operator, anal_date, status, id_auto, file_id, samples):
        # check key
        self.method = method
        self.equipment = equip
        self.conditions = conditions
        self.operator = operator
        self.date = anal_date
        self.status = status
        self.id_auto = id_auto
        self.file_id = file_id
        if isinstance(samples, Sample):
            self.samples.append(samples)
        elif isinstance(samples, list):
            for entry in samples:
                if not isinstance(entry, Sample):
                    raise Exception(f'Invalid sample: {entry}')
                    # Add "add sample?"
            self.samples = samples
        else:
            raise Exception('Invalid sample...')
            # Add "add sample?"
        # edit analysis

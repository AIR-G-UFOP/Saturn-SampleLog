import sys
import os
from datetime import date
from user_service import User


class Sample:
    def __init__(self):
        self.name = str
        self.description = str
        self.status = str
        self.date = date
        self.preparation = bool
        self.preparation_comment = str

    def addSample(self, name, descript, status, add_date, prep, prep_comment, user):
        if isinstance(user, User):
            self.name = name
            self.description = descript
            self.status = status
            self.date = add_date
            self.preparation = prep
            self.preparation_comment = prep_comment
            # user here
            # Need to generate a unique key for each sample
            # save sample to database
        else:
            raise Exception(f'Invalid User: {user}')
            # call an "add user?"

    def deleteSample(self, key):
        # test key
        # delete sample
        pass

    def editSample(self, key, name, descript, status, add_date, prep, prep_comment, user):
        # test key
        if isinstance(user, User):
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

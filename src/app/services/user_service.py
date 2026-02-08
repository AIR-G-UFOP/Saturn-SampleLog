import sys
import os


class User:
    def __init__(self):
        self.first_name = str
        self.surname = str
        self.org = str
        self.phone = str
        self.email = str

    def addUser(self, f_name, s_name, org, phone, email):
        self.first_name = f_name
        self.surname = s_name
        self.phone = phone
        self.email = email
        # Need to generate a unique key for each user
        # save user to database

    def deleteUser(self, key):
        # Test key
        # Delete user
        pass

    def editUser(self, key, f_name, s_name, org, phone, email):
        # Test key
        self.first_name = f_name
        self.surname = s_name
        self.org = org
        self.phone = phone
        self.email = email
        # edit user
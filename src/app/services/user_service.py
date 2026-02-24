import sys
import os


class UserService:
    def __init__(self):
        self.first_name = str
        self.surname = str
        self.org = str
        self.phone = str
        self.email = str
        self.address = str

    def addUser(self, user_info):
        self.first_name = user_info.get("name", "")
        self.surname = user_info.get("surname", "")
        self.org = user_info.get("organisation", "")
        self.phone = user_info.get("phone", "")
        self.email = user_info.get("email", "")
        self.address = user_info.get("address", "")

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

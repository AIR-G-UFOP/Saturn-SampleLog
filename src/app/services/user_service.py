import sys
import os
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from ..db.models import DbUser, DbSample, DbAnalysis
from ..db.session import SessionLocal


class UserService:

    def addUser(self, user_info):
        session = SessionLocal()
        try:
            new_user = DbUser(
                first_name = user_info["first_name"],
                surname = user_info["surname"],
                org = user_info["org"],
                phone = user_info["phone"],
                email = user_info["email"],
                address = user_info["address"])
            session.add(new_user)
            session.commit()
            return "User added successfully."
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error adding user: {str(e)}", file=sys.stderr)
            return "Error adding user. Please try again."
        finally:
            session.close()

    def deleteUser(self, key):
        # Test key
        # Delete user
        pass

    def editUser(self, user_id, user_info):
        session = SessionLocal()
        try:
            user = session.get(DbUser, user_id)
            user.first_name = user_info["first_name"]
            user.surname = user_info["surname"]
            user.org = user_info["org"]
            user.phone = user_info["phone"]
            user.email = user_info["email"]
            user.address = user_info["address"]
            session.commit()
            return "User updated successfully."
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error updating user: {str(e)}", file=sys.stderr)
            return "Error updating user. Please try again."
        finally:
            session.close()

    def getAllUsers(self):
        session = SessionLocal()
        try:
            users = session.query(DbUser).all()
            return users
        except SQLAlchemyError as e:
            print(f"Error retrieving users: {str(e)}", file=sys.stderr)
            return []
        finally:
            session.close()

    def getAllUsersFull(self):
        session = SessionLocal()
        try:
            users = (
                session.query(DbUser)
                .options(
                    selectinload(DbUser.samples)
                    .selectinload(DbSample.analyses)
                    .selectinload(DbAnalysis.reduction)
                )
                .all()
            )
            return users
        finally:
            session.close()

    def findUserById(self, user_id):
        session = SessionLocal()
        try:
            user = session.get(DbUser, user_id)
            return user
        finally:
            session.close()

from app.db.session import SessionLocal
from app.db.models import DbUser, DbSample, DbAnalysis, DbReduction

session = SessionLocal()
users = session.query(DbUser).all()
for user in users:
    print(f"Id: {user.id} User: {user.first_name} {user.surname}, Org: {user.org}, Email: {user.email}")
session.close()
from app.db.session import SessionLocal
from app.db.models import DbSample

session = SessionLocal()
samples = session.query(DbSample).all()
for sample in samples:
    print(f"Id: {sample.id} User_id: {sample.user_id}, name: {sample.name}")
session.close()
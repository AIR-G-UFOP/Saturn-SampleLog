from app.db.session import SessionLocal
from app.db.models import DbAnalysis, SampleAnalysis

session = SessionLocal()
analyses = session.query(DbAnalysis).all()
for anal in analyses:
    print(f"Id: {anal.id} method: {anal.method}")
session.close()

smpanal = session.query(SampleAnalysis).all()
for sa in smpanal:
    print(f"sample_id: {sa.sample_id}, analysis_id: {sa.analysis_id}")
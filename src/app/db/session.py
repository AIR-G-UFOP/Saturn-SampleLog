"""
This module sets up the SQLAlchemy session for database interactions. It creates a session factory that can be used to
create sessions for querying and manipulating the database. The session is configured to not autoflush, not autocommit,
and not expire on commit, which allows for more control over when changes are flushed to the database and when
transactions are committed.
"""


from sqlalchemy.orm import sessionmaker
from .engine import engine

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)

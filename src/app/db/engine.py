"""
This module sets up the SQLAlchemy engine for database interactions.
It imports the necessary components and creates an engine instance using the database URL from the configuration
settings.
"""


from sqlalchemy import create_engine
from ..config.settings import DATABASE_URL

engine = create_engine(DATABASE_URL, future=True)

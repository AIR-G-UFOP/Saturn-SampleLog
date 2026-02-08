from .base import Base
from .engine import engine
from . import models


def init_db():
    Base.metadata.create_all(
        bind=engine
    )
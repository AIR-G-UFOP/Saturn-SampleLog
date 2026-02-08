"""
This module defines the database models for the application using SQLAlchemy ORM. It includes the following classes:

- DbUser: Represents a user in the system, with attributes such as first name, surname, organization, phone, and email.
It has a one-to-many relationship with DbSample.

- DbSample: Represents a sample, with attributes such as name, description, date, user_id, preparation status, comment,
and status. It has a many-to-one relationship with DbUser and a one-to-many relationship with DbAnalysis.

- DbAnalysis: Represents an analysis, with attributes such as method, equipment, conditions, operator, date, file name,
and status. It has a many-to-many relationship with DbSample and a one-to-many relationship with DbReduction.

- DbReduction: Represents a reduction, with attributes such as software, software version, handler, date, notes,
file ID, status, and analysis_id. It has a many-to-one relationship with DbAnalysis.
"""


from .base import Base
from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship


class SampleAnalysis(Base):
    __tablename__ = 'sample_analysis'
    sample_id = Column(Integer, ForeignKey('samples.id'), primary_key=True)
    analysis_id = Column(Integer, ForeignKey('analyses.id'), primary_key=True)


class DbUser(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    org = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=False)

    samples = relationship('DbSamples', back_populates='users', cascade='all, delete-orphan')


class DbSample(Base):
    __tablename__ = 'samples'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    preparation = Column(Boolean, nullable=False)
    comment = Column(String, nullable=True)
    status = Column(String, nullable=False)

    users = relationship('DbUser', back_populates='samples')
    analyses = relationship('DbAnalysis', back_populates='samples')


class DbAnalysis(Base):
    __tablename__ = 'analyses'
    id = Column(Integer, primary_key=True)
    method = Column(String, nullable=False)
    equipment = Column(String, nullable=False)
    conditions = Column(String, nullable=False)
    operator = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    file_name = Column(String, nullable=False)
    status = Column(String, nullable=False)

    samples = relationship('DbSample', back_populates='analyses')
    reductions = relationship('DbAnalyses', back_populates='analyses', cascade='all, delete-orphan')


class DbReduction(Base):
    __tablename__ = 'reductions'
    id = Column(Integer, primary_key=True)
    software = Column(String, nullable=False)
    software_version = Column(String, nullable=False)
    handler = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    notes = Column(String, nullable=False)
    file_id = Column(String, nullable=False)
    status = Column(String, nullable=False)
    analysis_id = Column(Integer, ForeignKey('analyses.id'), unique=True, nullable=False)


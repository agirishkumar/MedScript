# app/db/models/patient_details.py

'''
Defines the PatientDetails model for storing detailed patient information and establishing relationships in the database.
'''

from sqlalchemy import Column, Integer, String, Date, DateTime, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..base import Base


class PatientDetails(Base):
    __tablename__ = "PatientDetails"

    PatientID = Column(Integer, primary_key=True, index=True)
    FirstName = Column(String(50), nullable=False)
    LastName = Column(String(50), nullable=False)
    DateOfBirth = Column(Date, nullable=False)
    Gender = Column(String(50), nullable=False)
    Address = Column(String(255), nullable=False)
    ContactNumber = Column(String(15), nullable=False)
    Email = Column(String(100), unique=True, index=True)
    Height = Column(Float, nullable=True)
    Weight = Column(Float, nullable=True)
    BloodType = Column(String(3), nullable=True)
    CreatedAt = Column(DateTime, server_default=func.now())

    symptoms = relationship("PatientSymptom", back_populates="patient", cascade="all, delete")
    visits = relationship("PatientVisit", back_populates="patient", cascade="all, delete")


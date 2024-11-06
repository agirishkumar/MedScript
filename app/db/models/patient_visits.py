# app/db/models/patient_visit.py

'''
Defines the PatientVisits model for storing detailed patient information and establishing relationships in the database.
'''

from sqlalchemy import Column, Integer, String, Date, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..base import Base


class PatientVisit(Base):
    __tablename__ = "PatientVisits"

    VisitID = Column(Integer, primary_key=True, index=True)
    PatientID = Column(Integer, ForeignKey('PatientDetails.PatientID'), nullable=False)
    DoctorID = Column(Integer, ForeignKey('Doctors.DoctorID'), nullable=False)
    SymptomID = Column(Integer, ForeignKey('PatientSymptoms.SymptomID'), nullable=False)
    VisitDate = Column(Date, nullable=False)
    DoctorsReportPdfLink = Column(String(255))
    PatientFriendlyReportPdfLink = Column(String(255))
    Notes = Column(Text)
    CreatedAt = Column(DateTime, server_default=func.now())

    patient = relationship("PatientDetails", back_populates="visits", cascade="all, delete")
    doctor = relationship("Doctor", back_populates="visits", cascade="all, delete")
    symptom = relationship("PatientSymptom", back_populates="visits", cascade="all, delete")

from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..base import Base


class PatientSymptom(Base):
    __tablename__ = "PatientSymptoms"

    SymptomID = Column(Integer, primary_key=True, index=True)
    PatientID = Column(Integer, ForeignKey('PatientDetails.PatientID'), nullable=False)
    SymptomDescription = Column(Text, nullable=False)
    ModelInputDescription = Column(Text, nullable=False)
    SymptomEnteredDate = Column(DateTime, server_default=func.now())

    patient = relationship("PatientDetails", back_populates="symptoms", cascade="all, delete")
    visits = relationship("PatientVisit", back_populates="symptom", cascade="all, delete")
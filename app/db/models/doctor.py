from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..base import Base


class Doctor(Base):
    __tablename__ = "Doctors"

    DoctorID = Column(Integer, primary_key=True, index=True)
    FirstName = Column(String(50), nullable=False)
    LastName = Column(String(50), nullable=False)
    Specialty = Column(String(100), nullable=False)
    LicenseNumber = Column(String(50), nullable=False)
    ContactNumber = Column(String(15), nullable=False)
    Email = Column(String(100), unique=True, index=True)
    CreatedAt = Column(DateTime, server_default=func.now())

    visits = relationship("PatientVisit", back_populates="doctor", cascade="all, delete")

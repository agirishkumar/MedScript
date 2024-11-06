# app/db/models/patient.py

'''
Defines the Patients model for storing doctor-related information and establishing relationships in the database.
'''

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..base import Base 

class Patient(Base):
    __tablename__ = "Patients"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('AppUsers.user_id'))
    name = Column(String, index=True)
    age = Column(Integer)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="patient", cascade="all, delete")

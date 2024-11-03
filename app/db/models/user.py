from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from ..base import Base 
from enum import Enum as PyEnum

class Role(PyEnum):
    PATIENT = 1
    DOCTOR = 2

class User(Base):
    __tablename__ = "AppUsers"

    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(Enum(Role), nullable=False)
    
    # Establish relationships to patient, doctor models
    patient = relationship("Patient", uselist=False, back_populates="user", cascade="all, delete")

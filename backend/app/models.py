from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    medical_record_number = Column(String(50), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    readings = relationship("PatientReading", back_populates="patient")
    predictions = relationship("Prediction", back_populates="patient")

class PatientReading(Base):
    __tablename__ = "patient_readings"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    blood_pressure = Column(String(20), nullable=False)  # e.g., "120/80"
    heart_rate = Column(Integer, nullable=False)
    temperature = Column(Float, nullable=False)
    oxygen_saturation = Column(Float, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    patient = relationship("Patient", back_populates="readings")

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)  # LOW, MEDIUM, HIGH
    recommendation = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    patient = relationship("Patient", back_populates="predictions")
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

# Patient schemas
class PatientBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=0, le=150)
    medical_record_number: str = Field(..., min_length=1, max_length=50)

class PatientCreate(PatientBase):
    pass

class Patient(PatientBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Patient Reading schemas
class MetricsBase(BaseModel):
    blood_pressure: str = Field(..., pattern=r'^\d{2,3}/\d{2,3}$')  # e.g., "120/80"
    heart_rate: int = Field(..., ge=30, le=300)
    temperature: float = Field(..., ge=90.0, le=110.0)
    oxygen_saturation: float = Field(..., ge=70.0, le=100.0)

class MetricsCreate(MetricsBase):
    pass

class PatientReading(MetricsBase):
    id: int
    patient_id: int
    recorded_at: datetime
    
    class Config:
        from_attributes = True

# Prediction schemas
class PredictionBase(BaseModel):
    risk_score: float = Field(..., ge=0.0, le=1.0)
    risk_level: str = Field(..., pattern=r'^(LOW|MEDIUM|HIGH)$')
    recommendation: str

class Prediction(PredictionBase):
    id: int
    patient_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class PredictionRequest(BaseModel):
    patient_id: int

# Response schemas
class PatientWithReadings(Patient):
    readings: List[PatientReading] = []
    predictions: List[Prediction] = []

class PaginatedPatients(BaseModel):
    patients: List[Patient]
    total: int
    page: int
    per_page: int
    total_pages: int

class APIResponse(BaseModel):
    status: str
    message: str
    data: Optional[dict] = None
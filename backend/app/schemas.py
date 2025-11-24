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
    heart_rate: int = Field(..., ge=0, le=300)  # Allow wider range for audit to catch
    temperature: float = Field(..., ge=0.0, le=200.0)  # Allow wider range for audit to catch
    oxygen_saturation: float = Field(..., ge=0.0, le=100.0)

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
    baseline_analysis: Optional[str] = None

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

class TriageScore(BaseModel):
    id: int
    patient_id: int
    name: str
    urgency_score: float
    reason: str
    current_risk: str
    trend: str

class APIResponse(BaseModel):
    status: str
    message: str
    data: Optional[dict] = None
    warning: Optional[str] = None
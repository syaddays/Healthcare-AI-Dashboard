from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
import math

from .database import get_db, create_tables
from .models import Patient, PatientReading, Prediction
from .schemas import (
    PatientCreate, Patient as PatientSchema, 
    MetricsCreate, PatientReading as ReadingSchema,
    Prediction as PredictionSchema, PredictionRequest,
    PatientWithReadings, PaginatedPatients, APIResponse
)
from .predictor import calculate_risk, get_latest_reading_for_prediction

# Create FastAPI app
app = FastAPI(
    title="Healthcare AI Dashboard API",
    description="A FastAPI backend for patient data management and AI-based health predictions",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Create database tables on startup"""
    await create_tables()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Healthcare AI Dashboard API", "status": "running"}

@app.post("/api/v1/patients", response_model=PatientSchema)
async def create_patient(patient: PatientCreate, db: AsyncSession = Depends(get_db)):
    """Create a new patient"""
    try:
        # Check if medical record number already exists
        result = await db.execute(
            select(Patient).where(Patient.medical_record_number == patient.medical_record_number)
        )
        existing_patient = result.scalar_one_or_none()
        
        if existing_patient:
            raise HTTPException(
                status_code=400, 
                detail="Patient with this medical record number already exists"
            )
        
        # Create new patient
        db_patient = Patient(
            name=patient.name,
            age=patient.age,
            medical_record_number=patient.medical_record_number,
            created_at=datetime.utcnow()
        )
        
        db.add(db_patient)
        await db.commit()
        await db.refresh(db_patient)
        
        return db_patient
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating patient: {str(e)}")

@app.get("/api/v1/patients", response_model=PaginatedPatients)
async def list_patients(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List patients with pagination"""
    try:
        # Get total count
        count_result = await db.execute(select(func.count(Patient.id)))
        total = count_result.scalar()
        
        # Calculate pagination
        offset = (page - 1) * per_page
        total_pages = math.ceil(total / per_page)
        
        # Get patients
        result = await db.execute(
            select(Patient)
            .order_by(Patient.created_at.desc())
            .offset(offset)
            .limit(per_page)
        )
        patients = result.scalars().all()
        
        return PaginatedPatients(
            patients=patients,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching patients: {str(e)}")

@app.get("/api/v1/patients/{patient_id}", response_model=PatientWithReadings)
async def get_patient_details(patient_id: int, db: AsyncSession = Depends(get_db)):
    """Get patient details with readings and predictions"""
    try:
        # Get patient
        result = await db.execute(select(Patient).where(Patient.id == patient_id))
        patient = result.scalar_one_or_none()
        
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Get readings
        readings_result = await db.execute(
            select(PatientReading)
            .where(PatientReading.patient_id == patient_id)
            .order_by(PatientReading.recorded_at.desc())
        )
        readings = readings_result.scalars().all()
        
        # Get predictions
        predictions_result = await db.execute(
            select(Prediction)
            .where(Prediction.patient_id == patient_id)
            .order_by(Prediction.created_at.desc())
        )
        predictions = predictions_result.scalars().all()
        
        return PatientWithReadings(
            id=patient.id,
            name=patient.name,
            age=patient.age,
            medical_record_number=patient.medical_record_number,
            created_at=patient.created_at,
            readings=readings,
            predictions=predictions
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching patient details: {str(e)}")

@app.post("/api/v1/patients/{patient_id}/metrics", response_model=APIResponse)
async def log_metrics(
    patient_id: int, 
    metrics: MetricsCreate, 
    db: AsyncSession = Depends(get_db)
):
    """Log vital signs for a patient"""
    try:
        # Verify patient exists
        result = await db.execute(select(Patient).where(Patient.id == patient_id))
        patient = result.scalar_one_or_none()
        
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Create new reading
        reading = PatientReading(
            patient_id=patient_id,
            blood_pressure=metrics.blood_pressure,
            heart_rate=metrics.heart_rate,
            temperature=metrics.temperature,
            oxygen_saturation=metrics.oxygen_saturation,
            recorded_at=datetime.utcnow()
        )
        
        db.add(reading)
        await db.commit()
        await db.refresh(reading)
        
        return APIResponse(
            status="success",
            message="Vital signs logged successfully",
            data={"reading_id": reading.id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error logging metrics: {str(e)}")

@app.post("/api/v1/predictions", response_model=PredictionSchema)
async def get_ai_prediction(
    prediction_request: PredictionRequest, 
    db: AsyncSession = Depends(get_db)
):
    """Generate AI prediction for a patient based on latest vitals"""
    try:
        patient_id = prediction_request.patient_id
        
        # Verify patient exists
        result = await db.execute(select(Patient).where(Patient.id == patient_id))
        patient = result.scalar_one_or_none()
        
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Get latest readings
        readings_result = await db.execute(
            select(PatientReading)
            .where(PatientReading.patient_id == patient_id)
            .order_by(PatientReading.recorded_at.desc())
            .limit(1)
        )
        latest_reading = readings_result.scalar_one_or_none()
        
        if not latest_reading:
            raise HTTPException(
                status_code=400, 
                detail="No vital signs data available for this patient"
            )
        
        # Calculate risk using AI predictor
        prediction_data = calculate_risk(
            heart_rate=latest_reading.heart_rate,
            blood_pressure=latest_reading.blood_pressure,
            temperature=latest_reading.temperature,
            oxygen_saturation=latest_reading.oxygen_saturation
        )
        
        # Save prediction to database
        prediction = Prediction(
            patient_id=patient_id,
            risk_score=prediction_data["risk_score"],
            risk_level=prediction_data["risk_level"],
            recommendation=prediction_data["recommendation"],
            created_at=datetime.utcnow()
        )
        
        db.add(prediction)
        await db.commit()
        await db.refresh(prediction)
        
        return prediction
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error generating prediction: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
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
    PatientWithReadings, PaginatedPatients, APIResponse, TriageScore
)
from .predictor import calculate_risk, get_latest_reading_for_prediction, audit_vitals

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
    """Log vital signs for a patient with data quality audit"""
    try:
        # Verify patient exists
        result = await db.execute(select(Patient).where(Patient.id == patient_id))
        patient = result.scalar_one_or_none()
        
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Audit vitals before saving
        audit_result = await audit_vitals({
            "heart_rate": metrics.heart_rate,
            "blood_pressure": metrics.blood_pressure,
            "temperature": metrics.temperature,
            "oxygen_saturation": metrics.oxygen_saturation
        })
        
        # Create new reading (save even if suspicious)
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
        
        # Prepare response with warning if data is suspicious
        warning = None
        if audit_result["status"] == "SUSPICIOUS":
            warning = f"Data flagged as suspicious: {audit_result['reason']}"
        
        return APIResponse(
            status="success",
            message="Vital signs logged successfully",
            data={"reading_id": reading.id},
            warning=warning
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
    """Generate AI prediction for a patient based on latest vitals with baseline comparison"""
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
        
        # Calculate historical average for personalized baseline
        avg_result = await db.execute(
            select(
                func.avg(PatientReading.heart_rate).label('avg_heart_rate'),
                func.avg(PatientReading.temperature).label('avg_temperature'),
                func.avg(PatientReading.oxygen_saturation).label('avg_oxygen_saturation')
            )
            .where(PatientReading.patient_id == patient_id)
        )
        avg_row = avg_result.first()
        
        historical_average = None
        if avg_row and avg_row.avg_heart_rate:
            historical_average = {
                "avg_heart_rate": float(avg_row.avg_heart_rate),
                "avg_temperature": float(avg_row.avg_temperature) if avg_row.avg_temperature else None,
                "avg_oxygen_saturation": float(avg_row.avg_oxygen_saturation) if avg_row.avg_oxygen_saturation else None
            }
        
        # Calculate risk using AI predictor with baseline
        prediction_data = await calculate_risk(
            heart_rate=latest_reading.heart_rate,
            blood_pressure=latest_reading.blood_pressure,
            temperature=latest_reading.temperature,
            oxygen_saturation=latest_reading.oxygen_saturation,
            historical_average=historical_average
        )
        
        # Save prediction to database (without baseline_analysis to avoid migration)
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
        
        # Return prediction with baseline_analysis (not saved to DB)
        return PredictionSchema(
            id=prediction.id,
            patient_id=prediction.patient_id,
            risk_score=prediction.risk_score,
            risk_level=prediction.risk_level,
            recommendation=prediction.recommendation,
            created_at=prediction.created_at,
            baseline_analysis=prediction_data.get("baseline_analysis")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error generating prediction: {str(e)}")

@app.get("/api/v1/triage", response_model=list[TriageScore])
async def get_triage_list(db: AsyncSession = Depends(get_db)):
    """Get prioritized patient list based on urgency scores"""
    try:
        # Get all patients
        patients_result = await db.execute(select(Patient))
        patients = patients_result.scalars().all()
        
        triage_scores = []
        
        for patient in patients:
            # Get last 2 readings for this patient
            readings_result = await db.execute(
                select(PatientReading)
                .where(PatientReading.patient_id == patient.id)
                .order_by(PatientReading.recorded_at.desc())
                .limit(2)
            )
            readings = readings_result.scalars().all()
            
            if not readings:
                continue
            
            # Calculate current risk score
            latest_reading = readings[0]
            current_risk_score = 0.0
            
            # Simple risk calculation
            if latest_reading.heart_rate > 100 or latest_reading.heart_rate < 60:
                current_risk_score += 0.3
            if latest_reading.temperature > 100.4 or latest_reading.temperature < 96.0:
                current_risk_score += 0.3
            if latest_reading.oxygen_saturation < 95:
                current_risk_score += 0.4
            
            current_risk_score = min(current_risk_score, 1.0)
            
            # Determine risk level
            if current_risk_score > 0.6:
                current_risk = "HIGH"
            elif current_risk_score > 0.3:
                current_risk = "MEDIUM"
            else:
                current_risk = "LOW"
            
            # Calculate rate of change (velocity)
            rate_of_change = 0.0
            trend = "STABLE"
            
            if len(readings) >= 2:
                older_reading = readings[1]
                
                # Calculate HR change
                hr_change = latest_reading.heart_rate - older_reading.heart_rate
                temp_change = latest_reading.temperature - older_reading.temperature
                spo2_change = older_reading.oxygen_saturation - latest_reading.oxygen_saturation  # Decrease is bad
                
                # Velocity score based on deterioration
                if abs(hr_change) > 20:
                    rate_of_change += 0.3
                if abs(temp_change) > 1.0:
                    rate_of_change += 0.2
                if spo2_change > 3:  # SpO2 dropping
                    rate_of_change += 0.3
                
                # Determine trend
                if hr_change > 20 or temp_change > 1.0 or spo2_change > 3:
                    trend = "DETERIORATING"
                elif hr_change < -20 or temp_change < -1.0 or spo2_change < -3:
                    trend = "IMPROVING"
            
            # Calculate urgency score: Current Risk + Rate of Change
            urgency_score = current_risk_score + rate_of_change
            
            # Build reason
            reason_parts = []
            if current_risk == "HIGH":
                reason_parts.append("High current risk")
            if trend == "DETERIORATING":
                reason_parts.append("Vitals deteriorating")
            elif trend == "IMPROVING":
                reason_parts.append("Vitals improving")
            if not reason_parts:
                reason_parts.append("Stable condition")
            
            reason = ", ".join(reason_parts)
            
            triage_scores.append(TriageScore(
                id=patient.id,
                patient_id=patient.id,
                name=patient.name,
                urgency_score=round(urgency_score, 2),
                reason=reason,
                current_risk=current_risk,
                trend=trend
            ))
        
        # Sort by urgency score (descending)
        triage_scores.sort(key=lambda x: x.urgency_score, reverse=True)
        
        return triage_scores
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating triage list: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
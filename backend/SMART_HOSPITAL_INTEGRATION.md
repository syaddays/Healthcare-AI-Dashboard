# Integration patch for Smart Hospital Features
# Instructions: Copy the code sections below into main.py in the appropriate locations

# 1. UPDATE IMPORTS (line 10-16)
# REPLACE:
# from .schemas import (
#     PatientCreate, Patient as PatientSchema, 
#     MetricsCreate, PatientReading as ReadingSchema,
#     Prediction as PredictionSchema, PredictionRequest,
#     PatientWithReadings, PaginatedPatients, APIResponse
# )
# from .predictor import calculate_risk, get_latest_reading_for_prediction

# WITH:
from .schemas import (
    PatientCreate, Patient as PatientSchema, 
    MetricsCreate, PatientReading as ReadingSchema,
    Prediction as PredictionSchema, PredictionRequest,
    PatientWithReadings, PaginatedPatients, APIResponse,
    TriageScore
)
from .predictor import calculate_risk, audit_vitals
from .smart_hospital import get_triage_list

# 2. UPDATE log_metrics ENDPOINT (line 158-197)
# REPLACE the entire log_metrics function with:
@app.post("/api/v1/patients/{patient_id}/metrics", response_model=APIResponse)
async def log_metrics(
    patient_id: int, 
    metrics: MetricsCreate, 
    db: AsyncSession = Depends(get_db)
):
    """Log vital signs for a patient with data audit"""
    try:
        # Verify patient exists
        result = await db.execute(select(Patient).where(Patient.id == patient_id))
        patient = result.scalar_one_or_none()
        
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # FEATURE 1: Data Auditor
        vitals_dict = {
            'heart_rate': metrics.heart_rate,
            'blood_pressure': metrics.blood_pressure,
            'temperature': metrics.temperature,
            'oxygen_saturation': metrics.oxygen_saturation
        }
        audit_result = await audit_vitals(vitals_dict)
        
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
        
        response = APIResponse(
            status="success",
            message="Vital signs logged successfully",
            data={"reading_id": reading.id}
        )
        
        if audit_result["status"] == "SUSPICIOUS":
            response.warning = f"⚠️ Data Quality Alert: {audit_result['reason']}"
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error logging metrics: {str(e)}")

# 3. UPDATE get_ai_prediction ENDPOINT (line 199-257)
# REPLACE the entire get_ai_prediction function with:
@app.post("/api/v1/predictions", response_model=PredictionSchema)
async def get_ai_prediction(
    prediction_request: PredictionRequest, 
    db: AsyncSession = Depends(get_db)
):
    """Generate AI prediction with personalized baseline"""
    try:
        patient_id = prediction_request.patient_id
        
        # Verify patient exists
        result = await db.execute(select(Patient).where(Patient.id == patient_id))
        patient = result.scalar_one_or_none()
        
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Get latest reading
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
        
        # FEATURE 2: Calculate historical averages for personalized baseline
        historical_average = None
        avg_result = await db.execute(
            select(
                func.avg(PatientReading.heart_rate).label('avg_hr'),
                func.avg(PatientReading.oxygen_saturation).label('avg_o2'),
                func.avg(PatientReading.temperature).label('avg_temp')
            )
            .where(PatientReading.patient_id == patient_id)
        )
        avg_row = avg_result.first()
        
        if avg_row and avg_row.avg_hr:
            historical_average = {
                'avg_hr': round(avg_row.avg_hr, 1),
                'avg_o2': round(avg_row.avg_o2, 1),
                'avg_temp': round(avg_row.avg_temp, 1)
            }
        
        # Calculate risk with personalized baseline
        prediction_data = await calculate_risk(
            heart_rate=latest_reading.heart_rate,
            blood_pressure=latest_reading.blood_pressure,
            temperature=latest_reading.temperature,
            oxygen_saturation=latest_reading.oxygen_saturation,
            historical_average=historical_average
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
        
        # Add baseline analysis to response
        if prediction_data.get("baseline_analysis"):
            prediction.baseline_analysis = prediction_data["baseline_analysis"]
        
        return prediction
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error generating prediction: {str(e)}")

# 4. ADD NEW TRIAGE ENDPOINT (insert before the "if __name__" line)
@app.get("/api/v1/triage", response_model=List[TriageScore])
async def get_triage(db: AsyncSession = Depends(get_db)):
    """FEATURE 3: Triage Officer - Get patients ranked by urgency"""
    return await get_triage_list(db)

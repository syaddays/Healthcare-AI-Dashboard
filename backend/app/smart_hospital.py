# Smart Hospital Extensions
# This file contains additional endpoints for the Smart Hospital features
# Import this in main.py with: from .smart_hospital import *

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
from typing import List

from .database import get_db
from .models import Patient, PatientReading, Prediction
from .schemas import TriageScore
from .predictor import audit_vitals

async def calculate_patient_triage_score(patient, latest_readings: List, last_prediction) -> dict:
    """
    Calculate urgency score for a single patient.
    Score = (Current Risk * 0.5) + (Trend Velocity * 0.5)
    """
    if not latest_readings or len(latest_readings) < 1:
        return {
            "patient_id": patient.id,
            "name": patient.name,
            "urgency_score": 0.0,
            "reason": "Insufficient data",
            "current_risk": 0.0,
            "trend": "N/A"
        }
    
    # Get current risk from latest prediction
    current_risk = last_prediction.risk_score if last_prediction else 0.5
    
    # Calculate trend velocity if we have 2+ readings
    trend_velocity = 0.0
    trend_desc = "Stable"
    
    if len(latest_readings) >= 2:
        # Calculate HR change rate
        try:
            hr1 = latest_readings[0].heart_rate
            hr2 = latest_readings[1].heart_rate
            time_diff = (latest_readings[0].recorded_at - latest_readings[1].recorded_at).total_seconds() / 3600
            
            if time_diff > 0:
                hr_rate = (hr1 - hr2) / time_diff  # bpm/hour
                
                # Normalize to 0-1 scale (assume +/- 20 bpm/hr is max concerning change)
                trend_velocity = min(abs(hr_rate) / 20.0, 1.0)
                
                if hr_rate > 5:
                    trend_desc = "Deteriorating"
                    trend_velocity *= 1.5  # Bonus for worsening
                elif hr_rate < -5:
                    trend_desc = "Improving"
                    trend_velocity *= 0.5  # Less urgent if improving
        except:
            pass
    
    # Final urgency score
    urgency_score = (current_risk * 0.5) + min(trend_velocity, 0.5)
    urgency_score = min(urgency_score, 1.0)
    
    return {
        "patient_id": patient.id,
        "name": patient.name,
        "urgency_score": round(urgency_score, 3),
        "reason": f"{trend_desc} trend, Current risk: {current_risk:.2f}",
        "current_risk": current_risk,
        "trend": trend_desc
    }

# This function can be imported into main.py to add the triage endpoint
async def get_triage_list(db: AsyncSession) -> List[TriageScore]:
    """
    FEATURE 3: Triage Officer - Rank patients by urgency
    """
    try:
        # Get all patients
        patients_result = await db.execute(select(Patient).order_by(Patient.id))
        patients = patients_result.scalars().all()
        
        triage_scores = []
        
        for patient in patients:
            # Get last 2 readings for trend analysis
            readings_result = await db.execute(
                select(PatientReading)
                .where(PatientReading.patient_id == patient.id)
                .order_by(PatientReading.recorded_at.desc())
                .limit(2)
            )
            readings = readings_result.scalars().all()
            
            # Get latest prediction
            prediction_result = await db.execute(
                select(Prediction)
                .where(Prediction.patient_id == patient.id)
                .order_by(Prediction.created_at.desc())
                .limit(1)
            )
            last_prediction = prediction_result.scalar_one_or_none()
            
            # Calculate triage score
            score_data = await calculate_patient_triage_score(patient, readings, last_prediction)
            triage_scores.append(TriageScore(**score_data))
        
        # Sort by urgency score (highest first)
        triage_scores.sort(key=lambda x: x.urgency_score, reverse=True)
        
        return triage_scores
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating triage: {str(e)}")

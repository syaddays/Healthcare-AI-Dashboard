from typing import Dict, Any

def calculate_risk(heart_rate: int, blood_pressure: str, temperature: float, oxygen_saturation: float) -> Dict[str, Any]:
    """
    Simple rule-based AI prediction for patient risk assessment.
    In a real application, this would be replaced with a trained ML model.
    """
    risk_score = 0.0
    
    # Parse systolic blood pressure (first number)
    try:
        systolic_bp = int(blood_pressure.split('/')[0])
    except (ValueError, IndexError):
        systolic_bp = 120  # Default normal value
    
    # Simple rule-based scoring
    if heart_rate > 100:
        risk_score += 0.3
    elif heart_rate < 60:
        risk_score += 0.2
        
    if systolic_bp > 140:
        risk_score += 0.3
    elif systolic_bp < 90:
        risk_score += 0.2
        
    if temperature > 100.4:  # Fever
        risk_score += 0.2
    elif temperature < 96.0:  # Hypothermia
        risk_score += 0.25
        
    if oxygen_saturation < 95:
        risk_score += 0.2
    elif oxygen_saturation < 90:
        risk_score += 0.4
    
    # Cap the risk score at 1.0
    risk_score = min(risk_score, 1.0)
    
    # Determine risk level and recommendation
    if risk_score > 0.6:
        risk_level = "HIGH"
        recommendation = "Immediate medical attention recommended. Multiple vital signs indicate potential health concerns."
    elif risk_score > 0.3:
        risk_level = "MEDIUM"
        recommendation = "Close monitoring advised. Some vital signs are outside normal ranges."
    else:
        risk_level = "LOW"
        recommendation = "Routine care. All vital signs appear within normal ranges."
    
    return {
        "risk_score": round(risk_score, 2),
        "risk_level": risk_level,
        "recommendation": recommendation
    }

def get_latest_reading_for_prediction(readings: list) -> Dict[str, Any]:
    """
    Get the most recent reading for prediction.
    In a real application, this might analyze trends over time.
    """
    if not readings:
        return None
    
    # Sort by recorded_at and get the latest
    latest_reading = max(readings, key=lambda x: x.recorded_at)
    
    return calculate_risk(
        heart_rate=latest_reading.heart_rate,
        blood_pressure=latest_reading.blood_pressure,
        temperature=latest_reading.temperature,
        oxygen_saturation=latest_reading.oxygen_saturation
    )
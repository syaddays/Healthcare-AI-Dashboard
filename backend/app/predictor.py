import os
import json
import httpx
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"

async def audit_vitals(vitals: dict) -> dict:
    """
    Audit vital signs for data quality issues.
    Returns: {"status": "VALID"|"SUSPICIOUS", "reason": str}
    """
    heart_rate = vitals.get("heart_rate")
    temperature = vitals.get("temperature")
    
    # Rule Check (First): Physiologically impossible values
    if heart_rate and (heart_rate > 220 or heart_rate < 30):
        return {
            "status": "SUSPICIOUS",
            "reason": "Physiologically impossible heart rate"
        }
    
    if temperature and (temperature > 108):
        return {
            "status": "SUSPICIOUS",
            "reason": "Physiologically impossible temperature"
        }
    
    # AI Check (Second): Ask LLM if values are plausible
    if HF_API_KEY:
        try:
            headers = {"Authorization": f"Bearer {HF_API_KEY}"}
            
            prompt = f"""<s>[INST] You are a medical data quality expert. Analyze these vitals for plausibility:
            
            - Heart Rate: {vitals.get('heart_rate')} bpm
            - Blood Pressure: {vitals.get('blood_pressure')} mmHg
            - Temperature: {vitals.get('temperature')} F
            - Oxygen Saturation: {vitals.get('oxygen_saturation')} %
            
            Are these values plausible for a human patient? Answer with JSON only:
            {{"plausible": true/false, "reason": "brief explanation"}}
            [/INST]"""
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 100,
                    "return_full_text": False,
                    "temperature": 0.1
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(HF_API_URL, headers=headers, json=payload, timeout=10.0)
                
            if response.status_code == 200:
                result = response.json()
                generated_text = result[0]["generated_text"].strip()
                
                # Try to parse JSON response
                if "```json" in generated_text:
                    generated_text = generated_text.split("```json")[1].split("```")[0].strip()
                elif "```" in generated_text:
                    generated_text = generated_text.split("```")[1].split("```")[0].strip()
                
                ai_result = json.loads(generated_text)
                
                if not ai_result.get("plausible", True):
                    return {
                        "status": "SUSPICIOUS",
                        "reason": f"AI flagged: {ai_result.get('reason', 'Implausible values')}"
                    }
        except Exception as e:
            print(f"AI Audit Error: {str(e)}")
            # Fall through to offline mode
    
    # Fallback: Offline mode - assume valid if rules passed
    return {
        "status": "VALID",
        "reason": "Offline mode - basic validation passed"
    }

async def calculate_risk(heart_rate: int, blood_pressure: str, temperature: float, oxygen_saturation: float, historical_average: dict = None) -> Dict[str, Any]:
    """
    Calculate patient risk using Hugging Face LLM with baseline comparison.
    """
    if not HF_API_KEY:
        # Fallback to rule-based if no key
        return _calculate_risk_rule_based(heart_rate, blood_pressure, temperature, oxygen_saturation, historical_average)

    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    
    # Build prompt with baseline comparison if available
    baseline_info = ""
    if historical_average:
        baseline_info = f"""
    
    Patient Baseline (Historical Average):
    - Average Heart Rate: {historical_average.get('avg_heart_rate', 'N/A')} bpm
    - Average Temperature: {historical_average.get('avg_temperature', 'N/A')} F
    - Average Oxygen Saturation: {historical_average.get('avg_oxygen_saturation', 'N/A')} %
    
    Compare current vitals against this baseline. Is this a significant deviation?"""
    
    prompt = f"""<s>[INST] You are a medical AI assistant. Analyze the following patient vitals and provide a risk assessment.
    
    Current Vitals:
    - Heart Rate: {heart_rate} bpm
    - Blood Pressure: {blood_pressure} mmHg
    - Temperature: {temperature} F
    - Oxygen Saturation: {oxygen_saturation} %{baseline_info}
    
    Return a JSON object with exactly these fields:
    - "risk_score": a number between 0.0 and 1.0 representing the risk probability.
    - "risk_level": "LOW", "MEDIUM", or "HIGH".
    - "recommendation": a brief medical recommendation (max 2 sentences).
    - "baseline_analysis": a brief comparison to baseline if provided, or "No baseline data" if not.
    
    Do not include any other text. JSON only. [/INST]"""

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 250,
            "return_full_text": False,
            "temperature": 0.1
        }
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(HF_API_URL, headers=headers, json=payload, timeout=10.0)
            
        if response.status_code != 200:
            print(f"HF API Error: {response.text}")
            return _calculate_risk_rule_based(heart_rate, blood_pressure, temperature, oxygen_saturation)
            
        result = response.json()
        generated_text = result[0]["generated_text"]
        
        # Clean up text to ensure valid JSON
        json_str = generated_text.strip()
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0].strip()
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0].strip()
            
        prediction = json.loads(json_str)
        
        # Validate fields
        return {
            "risk_score": float(prediction.get("risk_score", 0.5)),
            "risk_level": prediction.get("risk_level", "MEDIUM").upper(),
            "recommendation": prediction.get("recommendation", "Consult a doctor."),
            "baseline_analysis": prediction.get("baseline_analysis", "No baseline comparison available")
        }
        
    except Exception as e:
        print(f"AI Prediction Error: {str(e)}")
        return _calculate_risk_rule_based(heart_rate, blood_pressure, temperature, oxygen_saturation, historical_average)

def _calculate_risk_rule_based(heart_rate: int, blood_pressure: str, temperature: float, oxygen_saturation: float, historical_average: dict = None) -> Dict[str, Any]:
    """
    Fallback rule-based calculation with baseline comparison.
    """
    risk_score = 0.0
    baseline_analysis = "Offline mode - no AI baseline comparison available"
    
    try:
        systolic_bp = int(blood_pressure.split('/')[0])
    except (ValueError, IndexError):
        systolic_bp = 120
    
    if heart_rate > 100 or heart_rate < 60: risk_score += 0.3
    if systolic_bp > 140 or systolic_bp < 90: risk_score += 0.3
    if temperature > 100.4 or temperature < 96.0: risk_score += 0.2
    if oxygen_saturation < 95: risk_score += 0.2
    
    # Baseline comparison (rule-based)
    if historical_average:
        avg_hr = historical_average.get('avg_heart_rate')
        if avg_hr:
            hr_deviation = abs(heart_rate - avg_hr)
            if hr_deviation > 30:
                risk_score += 0.2
                baseline_analysis = f"Offline mode: HR deviation of {hr_deviation:.1f} bpm from personal baseline ({avg_hr:.1f} bpm)"
            else:
                baseline_analysis = f"Offline mode: HR within {hr_deviation:.1f} bpm of personal baseline ({avg_hr:.1f} bpm)"
    
    risk_score = min(risk_score, 1.0)
    
    if risk_score > 0.6:
        risk_level = "HIGH"
        recommendation = "Immediate attention required. Vitals are unstable."
    elif risk_score > 0.3:
        risk_level = "MEDIUM"
        recommendation = "Monitor closely. Some values are abnormal."
    else:
        risk_level = "LOW"
        recommendation = "Vitals are within normal range."
    
    return {
        "risk_score": round(risk_score, 2),
        "risk_level": risk_level,
        "recommendation": recommendation,
        "baseline_analysis": baseline_analysis
    }

async def get_latest_reading_for_prediction(readings: list) -> Dict[str, Any]:
    """
    Get the most recent reading for prediction.
    """
    if not readings:
        return None
    
    latest_reading = max(readings, key=lambda x: x.recorded_at)
    
    return await calculate_risk(
        heart_rate=latest_reading.heart_rate,
        blood_pressure=latest_reading.blood_pressure,
        temperature=latest_reading.temperature,
        oxygen_saturation=latest_reading.oxygen_saturation
    )
import os
import json
import httpx
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"

async def calculate_risk(heart_rate: int, blood_pressure: str, temperature: float, oxygen_saturation: float) -> Dict[str, Any]:
    """
    Calculate patient risk using Hugging Face LLM.
    """
    if not HF_API_KEY:
        # Fallback to rule-based if no key
        return _calculate_risk_rule_based(heart_rate, blood_pressure, temperature, oxygen_saturation)

    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    
    prompt = f"""<s>[INST] You are a medical AI assistant. Analyze the following patient vitals and provide a risk assessment.
    
    Vitals:
    - Heart Rate: {heart_rate} bpm
    - Blood Pressure: {blood_pressure} mmHg
    - Temperature: {temperature} F
    - Oxygen Saturation: {oxygen_saturation} %
    
    Return a JSON object with exactly these fields:
    - "risk_score": a number between 0.0 and 1.0 representing the risk probability.
    - "risk_level": "LOW", "MEDIUM", or "HIGH".
    - "recommendation": a brief medical recommendation (max 2 sentences).
    
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
            "recommendation": prediction.get("recommendation", "Consult a doctor.")
        }
        
    except Exception as e:
        print(f"AI Prediction Error: {str(e)}")
        return _calculate_risk_rule_based(heart_rate, blood_pressure, temperature, oxygen_saturation)

def _calculate_risk_rule_based(heart_rate: int, blood_pressure: str, temperature: float, oxygen_saturation: float) -> Dict[str, Any]:
    """
    Fallback rule-based calculation.
    """
    risk_score = 0.0
    
    try:
        systolic_bp = int(blood_pressure.split('/')[0])
    except (ValueError, IndexError):
        systolic_bp = 120
    
    if heart_rate > 100 or heart_rate < 60: risk_score += 0.3
    if systolic_bp > 140 or systolic_bp < 90: risk_score += 0.3
    if temperature > 100.4 or temperature < 96.0: risk_score += 0.2
    if oxygen_saturation < 95: risk_score += 0.2
    
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
        "recommendation": recommendation
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
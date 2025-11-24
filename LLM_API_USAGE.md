# 🤖 LLM API Usage in Smart Hospital Dashboard

## 📍 Where We Use the LLM API

The LLM (Mistral-7B) is used in **2 places** in `backend/app/predictor.py`:

---

## 1️⃣ **Data Auditor - Plausibility Check**

### Location: `backend/app/predictor.py` - Line ~36-75

### Function: `audit_vitals(vitals: dict)`

**What it does:**
- Asks the LLM: "Are these vitals plausible for a human patient?"
- Used as a **second layer** of validation after rule-based checks
- Catches edge cases and sensor drift

**Code:**
```python
async def audit_vitals(vitals: dict) -> dict:
    # ... rule checks first ...
    
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
            
            # Call Hugging Face API
            async with httpx.AsyncClient() as client:
                response = await client.post(HF_API_URL, headers=headers, json=payload, timeout=10.0)
```

**When it's called:**
- Every time you log patient vitals via `POST /api/v1/patients/{id}/metrics`
- Only if rule-based checks pass
- Falls back to "VALID" if API unavailable

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/patients/1/metrics" \
  -H "Content-Type: application/json" \
  -d '{"heart_rate": 75, "blood_pressure": "120/80", "temperature": 98.6, "oxygen_saturation": 98.0}'
```

---

## 2️⃣ **Risk Prediction with Baseline Comparison**

### Location: `backend/app/predictor.py` - Line ~90-165

### Function: `calculate_risk(..., historical_average=None)`

**What it does:**
- Analyzes patient vitals and calculates risk score
- Compares current vitals against patient's personal baseline
- Provides medical recommendations

**Code:**
```python
async def calculate_risk(heart_rate: int, blood_pressure: str, temperature: float, 
                        oxygen_saturation: float, historical_average: dict = None):
    if not HF_API_KEY:
        return _calculate_risk_rule_based(...)  # Fallback
    
    # Build prompt with baseline comparison
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
    
    # Call Hugging Face API
    async with httpx.AsyncClient() as client:
        response = await client.post(HF_API_URL, headers=headers, json=payload, timeout=10.0)
```

**When it's called:**
- When you request a prediction via `POST /api/v1/predictions`
- Includes patient's historical baseline for personalized analysis
- Falls back to rule-based if API unavailable

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/predictions" \
  -H "Content-Type: application/json" \
  -d '{"patient_id": 1}'
```

---

## 🔧 API Configuration

### Location: `backend/app/predictor.py` - Line ~9-11

```python
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
```

### Model Used:
- **Model:** Mistral-7B-Instruct-v0.2
- **Parameters:** 7 billion
- **Provider:** Hugging Face Inference API
- **Endpoint:** https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2

---

## 📊 API Call Flow

### Flow 1: Logging Vitals (Data Auditor)
```
User logs vitals
    ↓
POST /api/v1/patients/{id}/metrics (main.py)
    ↓
audit_vitals() called (predictor.py)
    ↓
Rule Check: HR 30-220, Temp ≤108
    ↓ PASS
AI Check: Call Hugging Face API
    ↓
LLM analyzes plausibility
    ↓
Return {"status": "VALID" or "SUSPICIOUS"}
    ↓
Save vitals + warning (if suspicious)
```

### Flow 2: Getting Prediction (Risk Assessment)
```
User requests prediction
    ↓
POST /api/v1/predictions (main.py)
    ↓
Calculate historical baseline (SQL AVG)
    ↓
calculate_risk() called (predictor.py)
    ↓
Call Hugging Face API with baseline
    ↓
LLM analyzes risk + baseline deviation
    ↓
Return {risk_score, risk_level, recommendation, baseline_analysis}
    ↓
Save prediction + return to user
```

---

## 🔍 How to See LLM in Action

### Test 1: Data Auditor with LLM
```bash
# Set your API key
export HUGGINGFACE_API_KEY="your_key_here"

# Start server
cd Healthcare-AI-Dashboard/backend
python -m uvicorn app.main:app --reload

# Log vitals (LLM will check plausibility)
curl -X POST "http://localhost:8000/api/v1/patients/1/metrics" \
  -H "Content-Type: application/json" \
  -d '{"heart_rate": 75, "blood_pressure": "120/80", "temperature": 98.6, "oxygen_saturation": 98.0}'

# Check server logs - you'll see:
# "Calling Hugging Face API for plausibility check..."
```

### Test 2: Risk Prediction with LLM
```bash
# Request prediction (LLM will analyze with baseline)
curl -X POST "http://localhost:8000/api/v1/predictions" \
  -H "Content-Type: application/json" \
  -d '{"patient_id": 1}'

# Response will include AI-generated:
# - risk_score
# - risk_level
# - recommendation
# - baseline_analysis
```

---

## 🔄 Fallback Behavior (Without API Key)

### What happens if no API key?

**Data Auditor:**
```python
# Falls back to rule-based only
if not HF_API_KEY:
    return {"status": "VALID", "reason": "Offline mode - basic validation passed"}
```

**Risk Prediction:**
```python
# Falls back to rule-based calculation
if not HF_API_KEY:
    return _calculate_risk_rule_based(...)
    # Returns: {"risk_score": 0.5, "risk_level": "MEDIUM", 
    #           "recommendation": "...", "baseline_analysis": "Offline mode"}
```

**System still works!** Just without AI enhancement.

---

## 📝 API Request Details

### Request Format:
```python
payload = {
    "inputs": prompt,  # The medical question
    "parameters": {
        "max_new_tokens": 250,      # Max response length
        "return_full_text": False,  # Only return generated text
        "temperature": 0.1          # Low temp = more deterministic
    }
}
```

### Response Format:
```python
[
    {
        "generated_text": '{"risk_score": 0.65, "risk_level": "MEDIUM", ...}'
    }
]
```

---

## 💰 API Cost (Hugging Face)

### Free Tier:
- **30,000 characters/month** FREE
- Perfect for demos and testing
- No credit card required

### Paid Tier:
- **$9/month** for 1M characters
- **$0.06 per 1K characters** after that

### Your Usage:
- Each prediction: ~500 characters
- Each audit: ~300 characters
- **Estimate:** 60-100 API calls on free tier

---

## 🎯 Where LLM is NOT Used

### Triage Officer (No LLM)
- Pure mathematical calculation
- Urgency = Current Risk + Rate of Change
- No API calls needed
- Always works offline

**Location:** `backend/app/main.py` - Line ~302-410

```python
@app.get("/api/v1/triage")
async def get_triage_list(...):
    # Pure Python math - no LLM
    urgency_score = current_risk_score + rate_of_change
```

---

## 🔧 How to Get Hugging Face API Key

### Step 1: Create Account
1. Go to: https://huggingface.co/join
2. Sign up (free)
3. Verify email

### Step 2: Generate Token
1. Go to: https://huggingface.co/settings/tokens
2. Click "New token"
3. Name: "Smart Hospital API"
4. Type: "Read"
5. Click "Generate"
6. **Copy the token** (starts with `hf_...`)

### Step 3: Add to Your App
```bash
# Create .env file
cd Healthcare-AI-Dashboard/backend
echo "HUGGINGFACE_API_KEY=hf_your_token_here" > .env

# Restart server
python -m uvicorn app.main:app --reload
```

### Step 4: Verify It Works
```bash
# Check logs when making API calls
# You should see: "Calling Hugging Face API..."
# Instead of: "Offline mode"
```

---

## 📊 LLM Usage Summary

| Feature | Uses LLM? | Fallback | API Calls per Request |
|---------|-----------|----------|----------------------|
| **Data Auditor** | ✅ Yes | Rule-based | 1 (only if rules pass) |
| **Risk Prediction** | ✅ Yes | Rule-based | 1 |
| **Baseline Analysis** | ✅ Yes | Math-based | 0 (included in prediction) |
| **Triage Officer** | ❌ No | N/A | 0 (pure math) |

---

## 🎯 Key Takeaways

1. **LLM is used in 2 functions:**
   - `audit_vitals()` - Data quality check
   - `calculate_risk()` - Risk prediction with baseline

2. **Model:** Mistral-7B-Instruct-v0.2 (7 billion parameters)

3. **Provider:** Hugging Face Inference API

4. **Fallback:** System works without API key (rule-based mode)

5. **Cost:** FREE for demos (30K chars/month)

6. **Location:** All LLM code is in `backend/app/predictor.py`

---

## 🔍 Quick Reference

**To see LLM in action:**
```bash
# 1. Set API key
export HUGGINGFACE_API_KEY="hf_your_key"

# 2. Start server
python -m uvicorn app.main:app --reload

# 3. Watch logs for:
# "Calling Hugging Face API..."
# "AI Prediction: ..."
```

**To test without LLM:**
```bash
# 1. Don't set API key (or unset it)
unset HUGGINGFACE_API_KEY

# 2. Start server
python -m uvicorn app.main:app --reload

# 3. Watch logs for:
# "Offline mode - basic validation passed"
# "Fallback to rule-based calculation"
```

---

**The LLM enhances your app but isn't required - perfect for demos! 🚀**

# How to Test Smart Hospital Features

## Prerequisites

1. Make sure the backend server is running:
```bash
cd Healthcare-AI-Dashboard/backend
python -m uvicorn app.main:app --reload
```

2. The server should be accessible at `http://localhost:8000`

## Run Verification Script

Open a new terminal and run:

```bash
cd Healthcare-AI-Dashboard
python verify_smart_hospital.py
```

## Expected Output

If all features are working correctly, you should see:

```
============================================================
Smart Hospital Features Verification
============================================================
Target: http://localhost:8000
Timestamp: 2025-11-24 10:30:00
✓ Server is running

============================================================
TEST: Test 1: Data Auditor - Bad Sensor Detection
============================================================
ℹ Creating test patient...
✓ Patient created with ID: 1
ℹ Logging impossible temperature (150°F)...
ℹ Response status: 200
ℹ Response body: {...}
✓ PASSED: Data Auditor correctly flagged suspicious vitals
✓ Warning message: Data flagged as suspicious: Physiologically impossible temperature

============================================================
TEST: Test 2: Personalized Baseline - Athlete Check
============================================================
ℹ Creating athlete patient...
✓ Athlete patient created with ID: 2
ℹ Logging 3 baseline readings (HR=50)...
✓ Baseline readings logged
ℹ Logging elevated reading (HR=95)...
✓ Elevated reading logged
ℹ Requesting AI prediction...
✓ PASSED: Personalized Baseline analysis present
✓ Baseline analysis: HR of 95 bpm is 45 bpm above patient's baseline

============================================================
TEST: Test 3: Triage Officer - Resource Optimization
============================================================
ℹ Creating Patient A (stable vitals)...
✓ Patient A created with ID: 3
ℹ Logging stable vitals for Patient A (HR: 70 -> 70)...
✓ Patient A vitals logged
ℹ Creating Patient B (deteriorating vitals)...
✓ Patient B created with ID: 4
ℹ Logging deteriorating vitals for Patient B (HR: 70 -> 110)...
✓ Patient B vitals logged
ℹ Calling /api/v1/triage endpoint...
✓ PASSED: Triage Officer correctly prioritized deteriorating patient
✓ Patient B (deteriorating) at index 0
✓ Patient A (stable) at index 1

============================================================
TEST SUMMARY
============================================================
Data Auditor: PASSED
Personalized Baseline: PASSED
Triage Officer: PASSED

Total: 3/3 tests passed
All Smart Hospital features verified successfully!
```

## Manual Testing

You can also test the endpoints manually using curl or Postman:

### Test Data Auditor
```bash
# Create a patient
curl -X POST http://localhost:8000/api/v1/patients \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Patient", "age": 45, "medical_record_number": "MRN001"}'

# Log impossible vitals (should trigger warning)
curl -X POST http://localhost:8000/api/v1/patients/1/metrics \
  -H "Content-Type: application/json" \
  -d '{
    "heart_rate": 75,
    "blood_pressure": "120/80",
    "temperature": 150.0,
    "oxygen_saturation": 98.0
  }'
```

### Test Personalized Baseline
```bash
# Log multiple readings to establish baseline
curl -X POST http://localhost:8000/api/v1/patients/1/metrics \
  -H "Content-Type: application/json" \
  -d '{"heart_rate": 50, "blood_pressure": "110/70", "temperature": 98.6, "oxygen_saturation": 99.0}'

# Repeat 2 more times...

# Log elevated reading
curl -X POST http://localhost:8000/api/v1/patients/1/metrics \
  -H "Content-Type: application/json" \
  -d '{"heart_rate": 95, "blood_pressure": "120/80", "temperature": 98.6, "oxygen_saturation": 98.0}'

# Get prediction (should show baseline analysis)
curl -X POST http://localhost:8000/api/v1/predictions \
  -H "Content-Type: application/json" \
  -d '{"patient_id": 1}'
```

### Test Triage Officer
```bash
# After creating patients with various vitals, call triage
curl http://localhost:8000/api/v1/triage
```

## Troubleshooting

### Server not responding
- Check if the backend is running: `ps aux | grep uvicorn`
- Check the port: `netstat -an | grep 8000`
- Try restarting the server

### Database errors
- Delete the database file and restart: `rm backend/healthcare.db`
- The tables will be recreated on startup

### Import errors
- Make sure you're in the correct directory
- Check Python version: `python --version` (should be 3.8+)
- Install dependencies: `pip install -r requirements.txt`

### Hugging Face API errors
- Features will work in offline/demo mode without API key
- To use AI features, set `HUGGINGFACE_API_KEY` in `.env` file

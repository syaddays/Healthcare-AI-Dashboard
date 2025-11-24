#!/usr/bin/env python3
"""
Smart Hospital Features Verification Script
Tests: Data Auditor, Personalized Baseline, and Triage Officer
"""

import httpx
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000"
TIMEOUT = 10.0

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_test_header(test_name: str):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}TEST: {test_name}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")

def print_success(message: str):
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")

def print_failure(message: str):
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")

def print_info(message: str):
    print(f"{Colors.YELLOW}ℹ {message}{Colors.RESET}")

def create_patient(client: httpx.Client, name: str, age: int, mrn: str) -> dict:
    """Helper function to create a patient"""
    response = client.post(
        f"{BASE_URL}/api/v1/patients",
        json={
            "name": name,
            "age": age,
            "medical_record_number": mrn
        }
    )
    response.raise_for_status()
    return response.json()

def log_vitals(client: httpx.Client, patient_id: int, hr: int, bp: str = "120/80", 
               temp: float = 98.6, spo2: float = 98.0) -> dict:
    """Helper function to log vital signs"""
    response = client.post(
        f"{BASE_URL}/api/v1/patients/{patient_id}/metrics",
        json={
            "heart_rate": hr,
            "blood_pressure": bp,
            "temperature": temp,
            "oxygen_saturation": spo2
        }
    )
    return response

def test_data_auditor():
    """
    Test 1: The "Bad Sensor" Check (Data Auditor)
    Verifies that impossible vitals trigger a warning
    """
    print_test_header("Test 1: Data Auditor - Bad Sensor Detection")
    
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            # Create a test patient
            print_info("Creating test patient...")
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            patient = create_patient(
                client, 
                name="Test Patient Auditor",
                age=45,
                mrn=f"MRN-AUDIT-{timestamp}"
            )
            patient_id = patient["id"]
            print_success(f"Patient created with ID: {patient_id}")
            
            # Log impossible temperature (150°F)
            print_info("Logging impossible temperature (150°F)...")
            response = log_vitals(
                client,
                patient_id=patient_id,
                hr=75,
                temp=150.0  # Impossible temperature
            )
            
            # Verify response
            print_info(f"Response status: {response.status_code}")
            
            if response.status_code != 200:
                print_failure(f"Expected status 200, got {response.status_code}")
                return False
            
            data = response.json()
            print_info(f"Response body: {data}")
            
            # Check for warning field
            if "warning" not in data:
                print_failure("FAILED: 'warning' field not found in response")
                return False
            
            warning_text = data["warning"]
            if not warning_text.startswith("Data flagged as suspicious"):
                print_failure(f"FAILED: Warning text doesn't match expected format")
                print_failure(f"Expected: 'Data flagged as suspicious...'")
                print_failure(f"Got: '{warning_text}'")
                return False
            
            print_success("PASSED: Data Auditor correctly flagged suspicious vitals")
            print_success(f"Warning message: {warning_text}")
            return True
            
    except Exception as e:
        print_failure(f"Test failed with exception: {str(e)}")
        return False

def test_personalized_baseline():
    """
    Test 2: The "Athlete" Check (Personalized Baseline)
    Verifies that baseline analysis detects deviations from personal norms
    """
    print_test_header("Test 2: Personalized Baseline - Athlete Check")
    
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            # Create athlete patient
            print_info("Creating athlete patient...")
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            patient = create_patient(
                client,
                name="Athlete Patient",
                age=28,
                mrn=f"MRN-ATHLETE-{timestamp}"
            )
            patient_id = patient["id"]
            print_success(f"Athlete patient created with ID: {patient_id}")
            
            # Log 3 readings with low baseline HR (50 bpm)
            print_info("Logging 3 baseline readings (HR=50)...")
            for i in range(3):
                response = log_vitals(client, patient_id, hr=50)
                if response.status_code != 200:
                    print_failure(f"Failed to log reading {i+1}")
                    return False
            print_success("Baseline readings logged")
            
            # Log 1 reading with elevated HR (95 bpm - normal range but high for athlete)
            print_info("Logging elevated reading (HR=95)...")
            response = log_vitals(client, patient_id, hr=95)
            if response.status_code != 200:
                print_failure("Failed to log elevated reading")
                return False
            print_success("Elevated reading logged")
            
            # Request prediction
            print_info("Requesting AI prediction...")
            response = client.post(
                f"{BASE_URL}/api/v1/predictions",
                json={"patient_id": patient_id}
            )
            
            if response.status_code != 200:
                print_failure(f"Prediction request failed with status {response.status_code}")
                return False
            
            prediction = response.json()
            print_info(f"Prediction response: {prediction}")
            
            # Check for baseline_analysis field
            if "baseline_analysis" not in prediction:
                print_failure("FAILED: 'baseline_analysis' field not found in prediction")
                return False
            
            baseline_analysis = prediction["baseline_analysis"]
            if baseline_analysis is None:
                print_failure("FAILED: 'baseline_analysis' is null")
                return False
            
            print_success("PASSED: Personalized Baseline analysis present")
            print_success(f"Baseline analysis: {baseline_analysis}")
            return True
            
    except Exception as e:
        print_failure(f"Test failed with exception: {str(e)}")
        return False

def test_triage_officer():
    """
    Test 3: The "Triage" Check (Resource Optimization)
    Verifies that patients are sorted by urgency score
    """
    print_test_header("Test 3: Triage Officer - Resource Optimization")
    
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            
            # Create Patient A with stable vitals
            print_info("Creating Patient A (stable vitals)...")
            patient_a = create_patient(
                client,
                name="Stable Patient A",
                age=50,
                mrn=f"MRN-STABLE-{timestamp}"
            )
            patient_a_id = patient_a["id"]
            print_success(f"Patient A created with ID: {patient_a_id}")
            
            # Log stable vitals for Patient A (HR 70 -> 70)
            print_info("Logging stable vitals for Patient A (HR: 70 -> 70)...")
            log_vitals(client, patient_a_id, hr=70)
            log_vitals(client, patient_a_id, hr=70)
            print_success("Patient A vitals logged")
            
            # Create Patient B with deteriorating vitals
            print_info("Creating Patient B (deteriorating vitals)...")
            patient_b = create_patient(
                client,
                name="Deteriorating Patient B",
                age=65,
                mrn=f"MRN-DETERI-{timestamp}"
            )
            patient_b_id = patient_b["id"]
            print_success(f"Patient B created with ID: {patient_b_id}")
            
            # Log deteriorating vitals for Patient B (HR 70 -> 110)
            print_info("Logging deteriorating vitals for Patient B (HR: 70 -> 110)...")
            log_vitals(client, patient_b_id, hr=70)
            log_vitals(client, patient_b_id, hr=110)
            print_success("Patient B vitals logged")
            
            # Call triage endpoint
            print_info("Calling /api/v1/triage endpoint...")
            response = client.get(f"{BASE_URL}/api/v1/triage")
            
            if response.status_code != 200:
                print_failure(f"Triage endpoint failed with status {response.status_code}")
                return False
            
            triage_data = response.json()
            print_info(f"Triage response: {triage_data}")
            
            # Verify it's a list
            if not isinstance(triage_data, list):
                print_failure("FAILED: Triage response is not a list")
                return False
            
            if len(triage_data) < 2:
                print_failure(f"FAILED: Expected at least 2 patients, got {len(triage_data)}")
                return False
            
            # Find our patients in the triage list
            patient_a_index = None
            patient_b_index = None
            
            for idx, patient in enumerate(triage_data):
                if patient.get("id") == patient_a_id:
                    patient_a_index = idx
                    print_info(f"Patient A found at index {idx} with urgency_score: {patient.get('urgency_score')}")
                elif patient.get("id") == patient_b_id:
                    patient_b_index = idx
                    print_info(f"Patient B found at index {idx} with urgency_score: {patient.get('urgency_score')}")
            
            if patient_a_index is None or patient_b_index is None:
                print_failure("FAILED: Could not find both patients in triage list")
                return False
            
            # Verify Patient B (deteriorating) has higher urgency than Patient A (stable)
            if patient_b_index > patient_a_index:
                print_failure(f"FAILED: Patient B (deteriorating) at index {patient_b_index} should be before Patient A (stable) at index {patient_a_index}")
                return False
            
            print_success("PASSED: Triage Officer correctly prioritized deteriorating patient")
            print_success(f"Patient B (deteriorating) at index {patient_b_index}")
            print_success(f"Patient A (stable) at index {patient_a_index}")
            return True
            
    except Exception as e:
        print_failure(f"Test failed with exception: {str(e)}")
        return False

def main():
    """Run all verification tests"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}Smart Hospital Features Verification{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"Target: {BASE_URL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if server is running
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.get(f"{BASE_URL}/")
            if response.status_code != 200:
                print_failure("Server is not responding correctly")
                sys.exit(1)
            print_success("Server is running")
    except Exception as e:
        print_failure(f"Cannot connect to server: {str(e)}")
        print_info("Make sure the backend is running on http://localhost:8000")
        sys.exit(1)
    
    # Run tests
    results = {
        "Data Auditor": test_data_auditor(),
        "Personalized Baseline": test_personalized_baseline(),
        "Triage Officer": test_triage_officer()
    }
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}TEST SUMMARY{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{Colors.GREEN}PASSED{Colors.RESET}" if result else f"{Colors.RED}FAILED{Colors.RESET}"
        print(f"{test_name}: {status}")
    
    print(f"\n{Colors.BLUE}Total: {passed}/{total} tests passed{Colors.RESET}")
    
    if passed == total:
        print(f"{Colors.GREEN}All Smart Hospital features verified successfully!{Colors.RESET}")
        sys.exit(0)
    else:
        print(f"{Colors.RED}Some features are not working as expected.{Colors.RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()

-- Healthcare AI Dashboard Database Schema
-- PostgreSQL initialization script

-- Create patients table
CREATE TABLE IF NOT EXISTS patients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INTEGER NOT NULL CHECK (age >= 0 AND age <= 150),
    medical_record_number VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create patient_readings table
CREATE TABLE IF NOT EXISTS patient_readings (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    blood_pressure VARCHAR(20) NOT NULL,
    heart_rate INTEGER NOT NULL CHECK (heart_rate >= 30 AND heart_rate <= 300),
    temperature DECIMAL(4,1) NOT NULL CHECK (temperature >= 90.0 AND temperature <= 110.0),
    oxygen_saturation DECIMAL(4,1) NOT NULL CHECK (oxygen_saturation >= 70.0 AND oxygen_saturation <= 100.0),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create predictions table
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    risk_score DECIMAL(3,2) NOT NULL CHECK (risk_score >= 0.0 AND risk_score <= 1.0),
    risk_level VARCHAR(20) NOT NULL CHECK (risk_level IN ('LOW', 'MEDIUM', 'HIGH')),
    recommendation TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_patients_mrn ON patients(medical_record_number);
CREATE INDEX IF NOT EXISTS idx_patient_readings_patient_id ON patient_readings(patient_id);
CREATE INDEX IF NOT EXISTS idx_patient_readings_recorded_at ON patient_readings(recorded_at);
CREATE INDEX IF NOT EXISTS idx_predictions_patient_id ON predictions(patient_id);
CREATE INDEX IF NOT EXISTS idx_predictions_created_at ON predictions(created_at);

-- Insert sample data for testing
INSERT INTO patients (name, age, medical_record_number) VALUES
    ('John Smith', 45, 'MRN001'),
    ('Sarah Johnson', 32, 'MRN002'),
    ('Michael Brown', 67, 'MRN003')
ON CONFLICT (medical_record_number) DO NOTHING;

-- Insert sample readings
INSERT INTO patient_readings (patient_id, blood_pressure, heart_rate, temperature, oxygen_saturation, recorded_at) VALUES
    (1, '120/80', 72, 98.6, 98.0, CURRENT_TIMESTAMP - INTERVAL '2 hours'),
    (1, '125/85', 78, 99.1, 97.5, CURRENT_TIMESTAMP - INTERVAL '1 hour'),
    (1, '118/75', 70, 98.4, 98.2, CURRENT_TIMESTAMP),
    (2, '110/70', 65, 98.2, 99.0, CURRENT_TIMESTAMP - INTERVAL '3 hours'),
    (2, '115/75', 68, 98.8, 98.5, CURRENT_TIMESTAMP - INTERVAL '1 hour'),
    (3, '140/90', 85, 100.2, 95.0, CURRENT_TIMESTAMP - INTERVAL '4 hours'),
    (3, '145/95', 90, 100.8, 94.5, CURRENT_TIMESTAMP - INTERVAL '2 hours')
ON CONFLICT DO NOTHING;

-- Insert sample predictions
INSERT INTO predictions (patient_id, risk_score, risk_level, recommendation, created_at) VALUES
    (1, 0.15, 'LOW', 'Routine care. All vital signs appear within normal ranges.', CURRENT_TIMESTAMP - INTERVAL '30 minutes'),
    (2, 0.10, 'LOW', 'Routine care. All vital signs appear within normal ranges.', CURRENT_TIMESTAMP - INTERVAL '45 minutes'),
    (3, 0.75, 'HIGH', 'Immediate medical attention recommended. Multiple vital signs indicate potential health concerns.', CURRENT_TIMESTAMP - INTERVAL '1 hour')
ON CONFLICT DO NOTHING;
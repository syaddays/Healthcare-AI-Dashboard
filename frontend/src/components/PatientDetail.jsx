import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { patientAPI } from '../api';
import VitalsChart from './VitalsChart';
import AddVitalsModal from './AddVitalsModal';

function PatientDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [patient, setPatient] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showVitalsModal, setShowVitalsModal] = useState(false);
  const [predictionLoading, setPredictionLoading] = useState(false);

  const fetchPatientDetails = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await patientAPI.getPatientDetails(id);
      setPatient(data);
    } catch (err) {
      setError('Failed to fetch patient details');
      console.error('Error fetching patient details:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPatientDetails();
  }, [id]);

  const handleVitalsAdded = () => {
    setShowVitalsModal(false);
    fetchPatientDetails(); // Refresh patient data
  };

  const handleGetPrediction = async () => {
    if (!patient.readings || patient.readings.length === 0) {
      alert('No vital signs data available. Please log some vitals first.');
      return;
    }

    try {
      setPredictionLoading(true);
      await patientAPI.getPrediction(parseInt(id));
      fetchPatientDetails(); // Refresh to get new prediction
    } catch (err) {
      alert('Failed to generate prediction: ' + (err.response?.data?.detail || err.message));
    } finally {
      setPredictionLoading(false);
    }
  };

  const getRiskBadgeClass = (riskLevel) => {
    switch (riskLevel?.toLowerCase()) {
      case 'low': return 'risk-low';
      case 'medium': return 'risk-medium';
      case 'high': return 'risk-high';
      default: return 'risk-low';
    }
  };

  const getLatestVitals = () => {
    if (!patient.readings || patient.readings.length === 0) return null;
    return patient.readings[0]; // Readings are sorted by recorded_at desc
  };

  if (loading) {
    return <div className="loading">Loading patient details...</div>;
  }

  if (error) {
    return (
      <div className="error">
        {error}
        <button className="btn" onClick={() => navigate('/')} style={{ marginLeft: '10px' }}>
          Back to Patients
        </button>
      </div>
    );
  }

  if (!patient) {
    return (
      <div className="error">
        Patient not found
        <button className="btn" onClick={() => navigate('/')} style={{ marginLeft: '10px' }}>
          Back to Patients
        </button>
      </div>
    );
  }

  const latestVitals = getLatestVitals();
  const latestPrediction = patient.predictions && patient.predictions.length > 0 ? patient.predictions[0] : null;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <button className="btn btn-secondary" onClick={() => navigate('/')}>
          ← Back to Patients
        </button>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button 
            className="btn"
            onClick={() => setShowVitalsModal(true)}
          >
            Log Vitals
          </button>
          <button 
            className="btn btn-secondary"
            onClick={handleGetPrediction}
            disabled={predictionLoading}
          >
            {predictionLoading ? 'Generating...' : 'Get AI Prediction'}
          </button>
        </div>
      </div>

      {/* Patient Info */}
      <div className="card">
        <h2>{patient.name}</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginTop: '20px' }}>
          <div>
            <strong>Age:</strong> {patient.age} years
          </div>
          <div>
            <strong>Medical Record:</strong> {patient.medical_record_number}
          </div>
          <div>
            <strong>Patient Since:</strong> {new Date(patient.created_at).toLocaleDateString()}
          </div>
          <div>
            <strong>Total Readings:</strong> {patient.readings?.length || 0}
          </div>
        </div>
      </div>

      {/* Latest Vitals */}
      {latestVitals && (
        <div className="card">
          <h3>Latest Vital Signs</h3>
          <div className="vitals-summary">
            <div className="vital-item">
              <div className="vital-label">Blood Pressure</div>
              <div className="vital-value">{latestVitals.blood_pressure}</div>
            </div>
            <div className="vital-item">
              <div className="vital-label">Heart Rate</div>
              <div className="vital-value">{latestVitals.heart_rate} bpm</div>
            </div>
            <div className="vital-item">
              <div className="vital-label">Temperature</div>
              <div className="vital-value">{latestVitals.temperature}°F</div>
            </div>
            <div className="vital-item">
              <div className="vital-label">Oxygen Saturation</div>
              <div className="vital-value">{latestVitals.oxygen_saturation}%</div>
            </div>
          </div>
          <div style={{ color: '#666', fontSize: '0.9rem', marginTop: '10px' }}>
            Recorded: {new Date(latestVitals.recorded_at).toLocaleString()}
          </div>
        </div>
      )}

      {/* Latest AI Prediction */}
      {latestPrediction && (
        <div className="card">
          <h3>Latest AI Risk Assessment</h3>
          <div style={{ display: 'flex', alignItems: 'center', gap: '15px', marginBottom: '15px' }}>
            <span className={`risk-badge ${getRiskBadgeClass(latestPrediction.risk_level)}`}>
              {latestPrediction.risk_level} Risk
            </span>
            <span style={{ fontSize: '1.2rem', fontWeight: '600' }}>
              Score: {(latestPrediction.risk_score * 100).toFixed(0)}%
            </span>
          </div>
          <div style={{ marginBottom: '10px' }}>
            <strong>Recommendation:</strong> {latestPrediction.recommendation}
          </div>
          <div style={{ color: '#666', fontSize: '0.9rem' }}>
            Generated: {new Date(latestPrediction.created_at).toLocaleString()}
          </div>
        </div>
      )}

      {/* Vitals Chart */}
      {patient.readings && patient.readings.length > 0 && (
        <div className="card">
          <h3>Vital Signs Trends</h3>
          <VitalsChart readings={patient.readings} />
        </div>
      )}

      {/* No Data Message */}
      {(!patient.readings || patient.readings.length === 0) && (
        <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
          <h3>No vital signs recorded</h3>
          <p>Click "Log Vitals" to start tracking this patient's health data.</p>
        </div>
      )}

      {showVitalsModal && (
        <AddVitalsModal
          patientId={id}
          patientName={patient.name}
          onClose={() => setShowVitalsModal(false)}
          onVitalsAdded={handleVitalsAdded}
        />
      )}
    </div>
  );
}

export default PatientDetail;
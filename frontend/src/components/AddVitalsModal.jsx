import React, { useState } from 'react';
import { patientAPI } from '../api';

function AddVitalsModal({ patientId, patientName, onClose, onVitalsAdded }) {
  const [formData, setFormData] = useState({
    blood_pressure: '',
    heart_rate: '',
    temperature: '',
    oxygen_saturation: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const validateForm = () => {
    const { blood_pressure, heart_rate, temperature, oxygen_saturation } = formData;
    
    // Validate blood pressure format (e.g., "120/80")
    if (!blood_pressure.match(/^\d{2,3}\/\d{2,3}$/)) {
      throw new Error('Blood pressure must be in format "120/80"');
    }
    
    // Validate heart rate
    const hr = parseInt(heart_rate);
    if (isNaN(hr) || hr < 30 || hr > 300) {
      throw new Error('Heart rate must be between 30 and 300 bpm');
    }
    
    // Validate temperature
    const temp = parseFloat(temperature);
    if (isNaN(temp) || temp < 90 || temp > 110) {
      throw new Error('Temperature must be between 90°F and 110°F');
    }
    
    // Validate oxygen saturation
    const o2 = parseFloat(oxygen_saturation);
    if (isNaN(o2) || o2 < 70 || o2 > 100) {
      throw new Error('Oxygen saturation must be between 70% and 100%');
    }
    
    return {
      blood_pressure,
      heart_rate: hr,
      temperature: temp,
      oxygen_saturation: o2
    };
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const validatedData = validateForm();
      await patientAPI.logMetrics(parseInt(patientId), validatedData);
      onVitalsAdded();
    } catch (err) {
      setError(err.message || 'Failed to log vital signs');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal">
      <div className="modal-content">
        <div className="modal-header">
          <h2 className="modal-title">Log Vital Signs</h2>
          <button className="close-btn" onClick={onClose}>&times;</button>
        </div>

        <div style={{ marginBottom: '20px', color: '#666' }}>
          Patient: <strong>{patientName}</strong>
        </div>

        {error && (
          <div className="error">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="blood_pressure">Blood Pressure *</label>
            <input
              type="text"
              id="blood_pressure"
              name="blood_pressure"
              value={formData.blood_pressure}
              onChange={handleChange}
              placeholder="e.g., 120/80"
              pattern="^\d{2,3}/\d{2,3}$"
              title="Format: 120/80"
              required
            />
            <small style={{ color: '#666', fontSize: '0.8rem' }}>
              Format: systolic/diastolic (e.g., 120/80)
            </small>
          </div>

          <div className="form-group">
            <label htmlFor="heart_rate">Heart Rate (bpm) *</label>
            <input
              type="number"
              id="heart_rate"
              name="heart_rate"
              value={formData.heart_rate}
              onChange={handleChange}
              placeholder="e.g., 72"
              min="30"
              max="300"
              required
            />
            <small style={{ color: '#666', fontSize: '0.8rem' }}>
              Normal range: 60-100 bpm
            </small>
          </div>

          <div className="form-group">
            <label htmlFor="temperature">Temperature (°F) *</label>
            <input
              type="number"
              id="temperature"
              name="temperature"
              value={formData.temperature}
              onChange={handleChange}
              placeholder="e.g., 98.6"
              min="90"
              max="110"
              step="0.1"
              required
            />
            <small style={{ color: '#666', fontSize: '0.8rem' }}>
              Normal range: 97.8-99.1°F
            </small>
          </div>

          <div className="form-group">
            <label htmlFor="oxygen_saturation">Oxygen Saturation (%) *</label>
            <input
              type="number"
              id="oxygen_saturation"
              name="oxygen_saturation"
              value={formData.oxygen_saturation}
              onChange={handleChange}
              placeholder="e.g., 98"
              min="70"
              max="100"
              step="0.1"
              required
            />
            <small style={{ color: '#666', fontSize: '0.8rem' }}>
              Normal range: 95-100%
            </small>
          </div>

          <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', marginTop: '30px' }}>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={onClose}
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn"
              disabled={loading}
            >
              {loading ? 'Logging...' : 'Log Vitals'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default AddVitalsModal;
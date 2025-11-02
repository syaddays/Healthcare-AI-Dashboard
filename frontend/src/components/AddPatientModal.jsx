import React, { useState } from 'react';
import { patientAPI } from '../api';

function AddPatientModal({ onClose, onPatientAdded }) {
  const [formData, setFormData] = useState({
    name: '',
    age: '',
    medical_record_number: ''
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

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Validate form data
      if (!formData.name.trim()) {
        throw new Error('Name is required');
      }
      if (!formData.age || formData.age < 0 || formData.age > 150) {
        throw new Error('Please enter a valid age (0-150)');
      }
      if (!formData.medical_record_number.trim()) {
        throw new Error('Medical record number is required');
      }

      const patientData = {
        name: formData.name.trim(),
        age: parseInt(formData.age),
        medical_record_number: formData.medical_record_number.trim()
      };

      await patientAPI.createPatient(patientData);
      onPatientAdded();
    } catch (err) {
      if (err.response?.status === 400) {
        setError(err.response.data.detail || 'Patient with this medical record number already exists');
      } else {
        setError(err.message || 'Failed to create patient');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal">
      <div className="modal-content">
        <div className="modal-header">
          <h2 className="modal-title">Add New Patient</h2>
          <button className="close-btn" onClick={onClose}>&times;</button>
        </div>

        {error && (
          <div className="error">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="name">Full Name *</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="Enter patient's full name"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="age">Age *</label>
            <input
              type="number"
              id="age"
              name="age"
              value={formData.age}
              onChange={handleChange}
              placeholder="Enter age"
              min="0"
              max="150"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="medical_record_number">Medical Record Number *</label>
            <input
              type="text"
              id="medical_record_number"
              name="medical_record_number"
              value={formData.medical_record_number}
              onChange={handleChange}
              placeholder="Enter unique medical record number"
              required
            />
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
              {loading ? 'Creating...' : 'Create Patient'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default AddPatientModal;
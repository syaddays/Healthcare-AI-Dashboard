import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { patientAPI } from '../api';
import AddPatientModal from './AddPatientModal';

function PatientList() {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [pagination, setPagination] = useState({
    page: 1,
    per_page: 10,
    total: 0,
    total_pages: 0
  });
  
  const navigate = useNavigate();

  const fetchPatients = async (page = 1) => {
    try {
      setLoading(true);
      setError(null);
      const data = await patientAPI.getPatients(page, 10);
      setPatients(data.patients);
      setPagination({
        page: data.page,
        per_page: data.per_page,
        total: data.total,
        total_pages: data.total_pages
      });
    } catch (err) {
      setError('Failed to fetch patients. Please check if the backend server is running.');
      console.error('Error fetching patients:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPatients();
  }, []);

  const handlePatientClick = (patientId) => {
    navigate(`/patient/${patientId}`);
  };

  const handlePatientAdded = () => {
    setShowAddModal(false);
    fetchPatients(pagination.page); // Refresh current page
  };

  const handlePageChange = (newPage) => {
    fetchPatients(newPage);
  };

  if (loading) {
    return <div className="loading">Loading patients...</div>;
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <h2>Patient Dashboard</h2>
        <button 
          className="btn"
          onClick={() => setShowAddModal(true)}
        >
          Add New Patient
        </button>
      </div>

      {error && (
        <div className="error">
          {error}
        </div>
      )}

      {patients.length === 0 && !loading && !error ? (
        <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
          <h3>No patients found</h3>
          <p>Click "Add New Patient" to get started.</p>
        </div>
      ) : (
        <>
          <div className="patient-grid">
            {patients.map((patient) => (
              <div
                key={patient.id}
                className="card patient-card"
                onClick={() => handlePatientClick(patient.id)}
              >
                <div className="patient-name">{patient.name}</div>
                <div className="patient-info">Age: {patient.age}</div>
                <div className="patient-info">MRN: {patient.medical_record_number}</div>
                <div className="patient-info">
                  Added: {new Date(patient.created_at).toLocaleDateString()}
                </div>
              </div>
            ))}
          </div>

          {/* Pagination */}
          {pagination.total_pages > 1 && (
            <div style={{ display: 'flex', justifyContent: 'center', gap: '10px', marginTop: '30px' }}>
              <button
                className="btn"
                onClick={() => handlePageChange(pagination.page - 1)}
                disabled={pagination.page === 1}
                style={{ opacity: pagination.page === 1 ? 0.5 : 1 }}
              >
                Previous
              </button>
              
              <span style={{ 
                display: 'flex', 
                alignItems: 'center', 
                padding: '0 20px',
                color: '#666'
              }}>
                Page {pagination.page} of {pagination.total_pages}
              </span>
              
              <button
                className="btn"
                onClick={() => handlePageChange(pagination.page + 1)}
                disabled={pagination.page === pagination.total_pages}
                style={{ opacity: pagination.page === pagination.total_pages ? 0.5 : 1 }}
              >
                Next
              </button>
            </div>
          )}

          <div style={{ textAlign: 'center', marginTop: '20px', color: '#666' }}>
            Showing {patients.length} of {pagination.total} patients
          </div>
        </>
      )}

      {showAddModal && (
        <AddPatientModal
          onClose={() => setShowAddModal(false)}
          onPatientAdded={handlePatientAdded}
        />
      )}
    </div>
  );
}

export default PatientList;
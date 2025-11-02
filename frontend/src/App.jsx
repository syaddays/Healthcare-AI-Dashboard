import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import PatientList from './components/PatientList';
import PatientDetail from './components/PatientDetail';

function Navigation() {
  const location = useLocation();
  
  return (
    <div className="header">
      <div className="container">
        <h1>Healthcare AI Dashboard</h1>
        <nav className="nav">
          <Link 
            to="/" 
            className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
          >
            Patients
          </Link>
        </nav>
      </div>
    </div>
  );
}

function App() {
  return (
    <Router>
      <div className="App">
        <Navigation />
        <div className="container">
          <Routes>
            <Route path="/" element={<PatientList />} />
            <Route path="/patient/:id" element={<PatientDetail />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
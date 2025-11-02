# Healthcare AI Dashboard

A full-stack web application for patient data management and AI-based health risk predictions. Built with React.js, FastAPI, PostgreSQL, and Docker.

## 🚀 Features

- **Patient Management**: Create and manage patient records with medical information
- **Vital Signs Tracking**: Log and monitor patient vital signs (blood pressure, heart rate, temperature, oxygen saturation)
- **AI Risk Assessment**: Real-time health risk predictions based on vital signs data
- **Interactive Dashboard**: Visual charts and trends for patient health monitoring
- **RESTful API**: Async FastAPI backend with comprehensive endpoints
- **Responsive Design**: Modern, mobile-friendly user interface

## 🛠 Tech Stack

- **Frontend**: React.js, React Router, Recharts, Axios
- **Backend**: FastAPI, SQLAlchemy (async), Pydantic
- **Database**: PostgreSQL (production), SQLite (development)
- **Containerization**: Docker, Docker Compose
- **Deployment**: Ready for AWS EC2 deployment

## 📋 Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

## 🚀 Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd healthcare-ai-dashboard
   ```

2. **Start all services**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

4. **Stop services**
   ```bash
   docker-compose down
   ```

## 🔧 Local Development Setup

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the backend**
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm start
   ```

## 📊 API Endpoints

### Patients
- `POST /api/v1/patients` - Create new patient
- `GET /api/v1/patients` - List patients (with pagination)
- `GET /api/v1/patients/{id}` - Get patient details

### Vital Signs
- `POST /api/v1/patients/{id}/metrics` - Log vital signs

### AI Predictions
- `POST /api/v1/predictions` - Generate AI risk assessment

## 🧠 AI Prediction Logic

The system uses rule-based logic to assess patient risk:

- **Heart Rate**: Risk increases if >100 bpm or <60 bpm
- **Blood Pressure**: Risk increases if systolic >140 mmHg or <90 mmHg
- **Temperature**: Risk increases if >100.4°F (fever) or <96°F (hypothermia)
- **Oxygen Saturation**: Risk increases if <95% (significant if <90%)

**Risk Levels**:
- **LOW** (0.0-0.3): Routine care recommended
- **MEDIUM** (0.3-0.6): Close monitoring advised
- **HIGH** (0.6-1.0): Immediate medical attention recommended

## 🗄 Database Schema

### Patients Table
- `id` (Primary Key)
- `name` (VARCHAR 100)
- `age` (INTEGER)
- `medical_record_number` (VARCHAR 50, Unique)
- `created_at` (TIMESTAMP)

### Patient Readings Table
- `id` (Primary Key)
- `patient_id` (Foreign Key)
- `blood_pressure` (VARCHAR 20)
- `heart_rate` (INTEGER)
- `temperature` (DECIMAL)
- `oxygen_saturation` (DECIMAL)
- `recorded_at` (TIMESTAMP)

### Predictions Table
- `id` (Primary Key)
- `patient_id` (Foreign Key)
- `risk_score` (DECIMAL 0.0-1.0)
- `risk_level` (VARCHAR: LOW/MEDIUM/HIGH)
- `recommendation` (TEXT)
- `created_at` (TIMESTAMP)

## 🚀 AWS Deployment

### Prerequisites
- AWS EC2 instance (Ubuntu 20.04+)
- Security group allowing ports 22, 80, 443, 3000, 8000

### Deployment Steps

1. **Connect to EC2 instance**
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   ```

2. **Install Docker and Docker Compose**
   ```bash
   sudo apt update
   sudo apt install -y docker.io docker-compose
   sudo usermod -aG docker ubuntu
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

3. **Clone and deploy**
   ```bash
   git clone <your-repo-url>
   cd healthcare-ai-dashboard
   docker-compose up -d
   ```

4. **Access application**
   - Frontend: http://your-ec2-ip:3000
   - Backend: http://your-ec2-ip:8000

### Production Considerations

- Use environment variables for sensitive data
- Set up SSL certificates (Let's Encrypt)
- Configure proper firewall rules
- Set up monitoring and logging
- Use managed database service (RDS)
- Implement backup strategies

## 🧪 Testing the API

### Using curl

**Create a patient:**
```bash
curl -X POST "http://localhost:8000/api/v1/patients" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "age": 35,
    "medical_record_number": "MRN12345"
  }'
```

**Log vital signs:**
```bash
curl -X POST "http://localhost:8000/api/v1/patients/1/metrics" \
  -H "Content-Type: application/json" \
  -d '{
    "blood_pressure": "120/80",
    "heart_rate": 72,
    "temperature": 98.6,
    "oxygen_saturation": 98.0
  }'
```

**Get AI prediction:**
```bash
curl -X POST "http://localhost:8000/api/v1/predictions" \
  -H "Content-Type: application/json" \
  -d '{"patient_id": 1}'
```

## 📁 Project Structure

```
healthcare-ai-dashboard/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── database.py          # Database configuration
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── schemas.py           # Pydantic schemas
│   │   └── predictor.py         # AI prediction logic
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── PatientList.jsx
│   │   │   ├── PatientDetail.jsx
│   │   │   ├── AddPatientModal.jsx
│   │   │   ├── AddVitalsModal.jsx
│   │   │   └── VitalsChart.jsx
│   │   ├── App.jsx
│   │   ├── api.js               # API client
│   │   └── index.js
│   ├── package.json
│   └── Dockerfile
├── database/
│   └── schema.sql               # Database initialization
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎯 Resume Highlights

**Key Technical Achievements:**
- Implemented async FastAPI endpoints for non-blocking database operations
- Built responsive React dashboard with real-time data visualization
- Designed PostgreSQL schema with proper indexing for performance
- Created containerized application with Docker multi-stage builds
- Integrated AI-based health risk assessment system
- Deployed scalable architecture ready for cloud deployment

**Technologies Demonstrated:**
- **Backend**: FastAPI, SQLAlchemy (async), Pydantic validation
- **Frontend**: React.js, React Router, Recharts, Axios
- **Database**: PostgreSQL with optimized queries and indexing
- **DevOps**: Docker, Docker Compose, multi-stage builds
- **Cloud**: AWS-ready deployment configuration
# 🎲 D&D Initiative Tracker

A production-ready, full-stack web application for tracking D&D encounters with automated CI/CD deployment, comprehensive testing, and monitoring. Built with React, FastAPI, PostgreSQL, Docker, and Azure.

[![CI/CD Pipeline](https://github.com/L96Expanded/D-D-Initiative/actions/workflows/azure-app-service-deploy.yml/badge.svg)](https://github.com/L96Expanded/D-D-Initiative/actions)
[![Test Coverage](https://img.shields.io/badge/coverage-71%25-brightgreen)](./docs/TEST_COVERAGE_REPORT.md)

## ✨ Features

- **User Authentication**: Secure JWT-based authentication with bcrypt password hashing
- **Encounter Management**: Create, edit, and delete encounters with multiple creatures
- **Initiative Tracking**: Automatic sorting by initiative with turn-by-turn progression
- **Dual-Window System**: Separate DM control panel and player display window
- **Image Upload & Management**: Creature images with auto-fetch from D&D 5e API
- **Real-time Sync**: Display window updates automatically when DM makes changes
- **Mobile Responsive**: Works on phones, tablets, and desktops
- **Production Deployment**: Live on Azure with CI/CD pipeline
- **Comprehensive Testing**: 98 test cases with 71% code coverage
- **Monitoring**: Application Insights, custom metrics, and health checks

## 🛠️ Tech Stack

### Frontend
- React 18 + TypeScript
- Vite (build tool)
- Axios (API client)
- React Router (navigation)

### Backend
- FastAPI + Python 3.11
- SQLAlchemy 2.0 (async ORM)
- PostgreSQL 15
- JWT authentication
- Pytest (testing framework)

### DevOps & Infrastructure
- **Docker** & Docker Compose
- **CI/CD**: GitHub Actions
- **Deployment**: Azure App Service + Azure Static Web Apps
- **Monitoring**: Azure Application Insights
- **Database**: Azure PostgreSQL

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Git](https://git-scm.com/downloads)

### Automated Setup

**Windows:**
```powershell
git clone https://github.com/L96Expanded/D-D-Initiative.git
cd D-D-Initiative
powershell -ExecutionPolicy Bypass -File setup.ps1
```

**Mac/Linux:**
```bash
git clone https://github.com/L96Expanded/D-D-Initiative.git
cd D-D-Initiative
chmod +x setup.sh
./setup.sh
```

The script automatically:
- ✅ Checks Docker installation
- ✅ Generates secure credentials
- ✅ Creates `.env` file
- ✅ Builds and starts containers
- ✅ Opens browser to http://localhost:3000

### Manual Setup

```bash
# 1. Clone repository
git clone https://github.com/L96Expanded/D-D-Initiative.git
cd D-D-Initiative

# 2. Create environment file
cp .env.example .env
# Edit .env - change POSTGRES_PASSWORD and JWT_SECRET

# 3. Start with Docker Compose
docker-compose up --build -d

# 4. Access application
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

## 🧪 Running Tests

### Backend Tests (Pytest)

```bash
# Run all tests with coverage
cd backend
pytest tests/ -v --cov=app --cov-report=term-missing

# Run specific test file
pytest tests/test_encounters.py -v

# Run tests in Docker
docker-compose exec backend pytest tests/ -v

# Generate HTML coverage report
pytest tests/ --cov=app --cov-report=html
```

**Test Results:**
- Total Tests: 98
- Passing: 98 (100%)
- Coverage: 71% (exceeds 70% requirement)
- Test Suites: Authentication, Encounters, Creatures, Uploads, Users, Database

### Frontend Tests

```bash
cd frontend
npm test
```

## 🚢 Deployment

### Automated Deployment (CI/CD)

The project uses GitHub Actions for automated deployment:

1. **Push to main branch** triggers the CI/CD pipeline
2. **Backend tests run** (must pass for deployment)
3. **Docker images build** for backend and frontend
4. **Deploy to Azure**:
   - Backend → Azure App Service
   - Frontend → Azure Static Web Apps
5. **Health checks** verify deployment

### Manual Deployment

#### Deploy Backend to Azure App Service

```bash
# Login to Azure
az login

# Deploy backend
cd azure-infrastructure
./deploy-with-sp.ps1
```

#### Deploy Frontend to Azure Static Web Apps

Frontend deploys automatically via GitHub Actions when changes are pushed to main.

### Environment Variables for Production

Required environment variables (set in Azure App Service Configuration):

```env
DATABASE_URL=postgresql://user:password@host:5432/database
JWT_SECRET=your-secure-secret-key-64-characters-minimum
CORS_ORIGINS=["https://yourdomain.com"]
ENVIRONMENT=production
AZURE_APPLICATION_INSIGHTS_CONNECTION_STRING=your-connection-string
```

## 📊 Monitoring

### Application Insights (Azure)

The application integrates with Azure Application Insights for:
- Request/response tracking
- Performance metrics
- Error logging
- Custom events
- Dependency tracking

### Health Checks

```bash
# Check backend health
curl http://localhost:8000/api/health

# Check production health
curl https://dnd-initiative-prod.azurewebsites.net/api/health
```

### Metrics Endpoint

```bash
# View application metrics
curl http://localhost:8000/metrics
```

Metrics include:
- Request count by endpoint
- Response time percentiles
- Error rates
- Database query performance

### Monitoring Dashboard

Grafana dashboard configuration available in `monitoring/grafana-dashboard.json`

## 📁 Project Structure

```
D-D-Initiative/
├── frontend/              # React + TypeScript frontend
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Page components
│   │   ├── utils/         # API client, helpers
│   │   └── types/         # TypeScript definitions
│   ├── Dockerfile
│   └── package.json
│
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── models/        # SQLAlchemy models, Pydantic schemas
│   │   ├── routers/       # API endpoints
│   │   └── utils/         # Auth, metrics, storage
│   ├── tests/             # Pytest test suite (98 tests)
│   ├── Dockerfile
│   └── requirements.txt
│
├── azure-infrastructure/  # Infrastructure as Code (Bicep)
│   ├── main.bicep
│   └── modules/
│
├── .github/workflows/     # CI/CD pipelines
│   └── azure-app-service-deploy.yml
│
├── docs/                  # Documentation
│   ├── CODE_QUALITY_REVIEW.md
│   ├── DOCKER_DOCUMENTATION.md
│   ├── MONITORING_DOCUMENTATION.md
│   └── TEST_COVERAGE_REPORT.md
│
├── docker-compose.yml     # Local development setup
├── .env.example           # Environment template
├── README.md              # This file
├── REPORT.md              # DevOps improvements report
├── QUICKSTART.md          # Beginner setup guide
└── CONTRIBUTING.md        # Developer guidelines
```

## 🔧 Common Commands

```bash
# Start application
docker-compose up -d

# Stop application
docker-compose down

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart services
docker-compose restart

# Rebuild containers
docker-compose up --build -d

# Run tests
docker-compose exec backend pytest tests/ -v

# Check container status
docker-compose ps

# Access database
docker-compose exec postgres psql -U dnd_user -d dnd_tracker

# Clean up (removes all data!)
docker-compose down -v
```

## 🐛 Troubleshooting

### Port Conflicts
```bash
# If ports 3000, 8000, or 5432 are in use
# Option 1: Stop conflicting services
# Option 2: Change ports in docker-compose.yml
```

### Docker Not Running
```bash
# Ensure Docker Desktop is running
# Look for green whale icon in system tray
```

### Database Connection Errors
```bash
# Reset database
docker-compose down -v
docker-compose up -d
```

### Tests Failing
```bash
# Ensure dependencies are up to date
cd backend
pip install -r requirements-dev.txt
pytest tests/ -v
```

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute setup guide
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Development guidelines
- **[REPORT.md](REPORT.md)** - DevOps improvements summary
- **[docs/](docs/)** - Technical documentation
  - Code Quality Review
  - Docker Documentation
  - Monitoring Documentation
  - Test Coverage Report

## 🔐 Security

- JWT authentication with bcrypt password hashing
- CORS protection
- SQL injection prevention (SQLAlchemy ORM)
- XSS protection (React)
- Secure environment variable management
- Production secrets stored in Azure Key Vault

## 🎯 Production URLs

- **Frontend**: https://karsusinitiative.com
- **Backend API**: https://dnd-initiative-prod.azurewebsites.net
- **API Documentation**: https://dnd-initiative-prod.azurewebsites.net/docs

## 📄 License

This project is for educational purposes as part of a DevOps course assessment.

## 👥 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/L96Expanded/D-D-Initiative/issues)
- **Documentation**: See [docs/](docs/) folder

---

**Built with ❤️ for DMs and their adventuring parties** 🗡️✨

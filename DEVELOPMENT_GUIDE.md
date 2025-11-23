# D&D Initiative Tracker - Development Guide

This guide provides comprehensive instructions for running, testing, and deploying the D&D Initiative Tracker application with its new DevOps improvements.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Running Tests](#running-tests)
4. [Running the Application](#running-the-application)
5. [Monitoring Setup](#monitoring-setup)
6. [Deployment](#deployment)
7. [CI/CD Pipeline](#cicd-pipeline)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

- **Python 3.11+**: Backend runtime
- **Node.js 18+**: Frontend build tools
- **Docker Desktop**: Container runtime
- **Docker Compose**: Multi-container orchestration
- **Git**: Version control

### Optional Tools

- **VS Code**: Recommended IDE
- **Postman**: API testing
- **DBeaver**: Database management

---

## Local Development Setup

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd D-D-Initiative
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Create .env file (copy from .env.example)
cp .env.example .env

# Edit .env with your configuration
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env
```

### 4. Database Setup

```bash
# Using Docker Compose
cd ..
docker-compose up -d db

# The database will be initialized with init.sql
```

---

## Running Tests

### Backend Tests

```bash
cd backend

# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Run all tests with coverage
pytest tests/ -v --cov=app --cov-report=html --cov-report=term

# Run only unit tests
pytest tests/ -v -m "unit"

# Run only integration tests
pytest tests/ -v -m "integration"

# Run specific test file
pytest tests/test_models.py -v

# Generate coverage report
pytest tests/ --cov=app --cov-report=html
# Open htmlcov/index.html in browser to view detailed coverage

# Check if coverage meets 70% threshold
pytest tests/ --cov=app --cov-fail-under=70
```

### Test Output Locations

- **Terminal**: Real-time test results
- **HTML Report**: `backend/htmlcov/index.html`
- **Coverage JSON**: `backend/coverage.json`
- **JUnit XML**: `backend/test-results.xml`

### Frontend Tests

```bash
cd frontend

# Run linting
npm run lint

# Build verification
npm run build

# Run tests (if implemented)
npm test
```

---

## Running the Application

### Option 1: Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps

# Stop all services
docker-compose down
```

Services will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Database**: localhost:5432

### Option 2: Manual Development Mode

#### Terminal 1 - Backend
```bash
cd backend
.venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

#### Terminal 3 - Database
```bash
docker-compose up db
```

---

## Monitoring Setup

### Start Monitoring Stack

```bash
# Start Prometheus and Grafana
docker-compose -f docker-compose.monitoring.yml up -d

# Check status
docker-compose -f docker-compose.monitoring.yml ps
```

### Access Monitoring Tools

- **Prometheus**: http://localhost:9090
  - Metrics explorer
  - Query interface
  - Alert manager

- **Grafana**: http://localhost:3001
  - Default credentials: admin/admin
  - Pre-configured dashboards
  - Custom dashboard creation

### Available Metrics

Access raw metrics at: http://localhost:8000/api/metrics

Key metrics:
- `http_requests_total`: Total requests by endpoint
- `http_request_duration_seconds`: Request latency
- `http_errors_total`: Error counts
- `system_cpu_usage_percent`: CPU usage
- `system_memory_usage_bytes`: Memory usage

### Health Checks

```bash
# Main health check
curl http://localhost:8000/api/health

# Readiness probe
curl http://localhost:8000/api/health/ready

# Liveness probe
curl http://localhost:8000/api/health/live
```

---

## Deployment

### Prerequisites for Deployment

1. **GitHub Repository**: Code hosted on GitHub
2. **Docker Hub Account**: For container registry
3. **Production Server**: With Docker and Docker Compose installed
4. **Domain Name**: (Optional) For production access

### GitHub Secrets Configuration

Add these secrets to your GitHub repository:

```
Settings > Secrets and variables > Actions > New repository secret
```

Required secrets:
- `DOCKER_USERNAME`: Your Docker Hub username
- `DOCKER_PASSWORD`: Docker Hub access token
- `DEPLOY_HOST`: Production server IP/hostname
- `DEPLOY_USER`: SSH username for deployment
- `DEPLOY_SSH_KEY`: SSH private key (entire key including headers)
- `APP_URL`: Your application URL (e.g., https://dnd-tracker.example.com)
- `GRAFANA_PASSWORD`: Password for Grafana admin

### Manual Deployment Steps

```bash
# 1. Build Docker images
docker-compose -f docker-compose.prod.yml build

# 2. Tag images (optional, for versioning)
docker tag dnd-initiative-backend:latest yourusername/dnd-initiative-backend:v1.0.0
docker tag dnd-initiative-frontend:latest yourusername/dnd-initiative-frontend:v1.0.0

# 3. Push to Docker Hub
docker push yourusername/dnd-initiative-backend:v1.0.0
docker push yourusername/dnd-initiative-frontend:v1.0.0

# 4. On production server, pull and restart
ssh user@your-server
cd /opt/dnd-initiative
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# 5. Verify deployment
curl https://your-domain.com/api/health
```

### Automated Deployment (via CI/CD)

The application automatically deploys when you push to the `main` branch:

```bash
git add .
git commit -m "Your changes"
git push origin main

# GitHub Actions will:
# 1. Run all tests
# 2. Check code coverage (must be ≥70%)
# 3. Build Docker images
# 4. Push to Docker Hub
# 5. Deploy to production server
# 6. Run health checks
```

Monitor deployment progress:
- Go to your GitHub repository
- Click "Actions" tab
- View the running workflow

---

## CI/CD Pipeline

### Pipeline Stages

1. **Test Backend**
   - Install dependencies
   - Run linting (Flake8)
   - Run type checking (MyPy)
   - Execute unit tests
   - Execute integration tests
   - Verify code coverage ≥70%
   - Upload coverage reports

2. **Test Frontend**
   - Install dependencies
   - Run linting
   - Build verification

3. **Build Docker Images** (main branch only)
   - Build backend image
   - Build frontend image
   - Tag with version
   - Push to Docker Hub

4. **Deploy** (main branch only)
   - SSH to production server
   - Pull latest images
   - Restart services
   - Health check verification

### Pipeline Triggers

- **Push to main**: Full pipeline with deployment
- **Push to develop**: Tests only, no deployment
- **Pull requests**: Tests only, no deployment

### Viewing Pipeline Results

```bash
# Local testing before push
pytest tests/ --cov=app --cov-fail-under=70

# Check lint errors
flake8 app/ --count --show-source --statistics

# Type checking
mypy app/ --ignore-missing-imports
```

---

## Troubleshooting

### Tests Failing

```bash
# Clear cache and retry
pytest tests/ --cache-clear -v

# Run specific test for debugging
pytest tests/test_models.py::TestUserModel::test_user_creation -v -s

# Check test database
pytest tests/ -v --tb=long  # Show full tracebacks
```

### Coverage Below 70%

```bash
# Generate detailed coverage report
pytest tests/ --cov=app --cov-report=html

# Open htmlcov/index.html and look for:
# - Red lines (not covered)
# - Functions/classes with low coverage
# - Add tests for uncovered code
```

### Docker Issues

```bash
# Clean up Docker resources
docker-compose down -v  # Remove volumes
docker system prune -a  # Clean up unused resources

# Rebuild without cache
docker-compose build --no-cache

# View container logs
docker-compose logs backend
docker-compose logs frontend
```

### Database Connection Issues

```bash
# Check database is running
docker-compose ps db

# View database logs
docker-compose logs db

# Connect to database
docker-compose exec db psql -U postgres -d dnd_tracker

# Reset database
docker-compose down -v
docker-compose up -d db
```

### Monitoring Not Working

```bash
# Check Prometheus is scraping
# Visit: http://localhost:9090/targets
# All targets should show "UP"

# Restart monitoring stack
docker-compose -f docker-compose.monitoring.yml restart

# Check metrics endpoint
curl http://localhost:8000/api/metrics
```

### CI/CD Pipeline Failures

1. **Tests failing**: Fix tests locally first
2. **Coverage too low**: Add more tests
3. **Docker build failing**: Check Dockerfile syntax
4. **Deployment failing**: Verify GitHub secrets
5. **Health check failing**: Check application logs

### Common Error Messages

#### "Import could not be resolved"
- Ensure virtual environment is activated
- Run: `pip install -r requirements.txt requirements-dev.txt`

#### "Database connection refused"
- Start database: `docker-compose up -d db`
- Check connection string in .env file

#### "Permission denied" during deployment
- Verify SSH key is correct in GitHub secrets
- Check SSH key permissions: `chmod 600 ~/.ssh/id_rsa`

#### "Coverage failure: 65%"
- Add more tests
- Focus on uncovered lines shown in htmlcov/index.html

---

## Development Workflow

### Making Changes

```bash
# 1. Create feature branch
git checkout -b feature/your-feature

# 2. Make changes
# Edit code...

# 3. Run tests locally
pytest tests/ -v --cov=app --cov-fail-under=70

# 4. Format code
black app/ tests/

# 5. Lint code
flake8 app/

# 6. Commit changes
git add .
git commit -m "Description of changes"

# 7. Push branch
git push origin feature/your-feature

# 8. Create pull request on GitHub
# - Tests will run automatically
# - Merge after approval and passing tests
```

### Code Review Checklist

- [ ] Tests added for new functionality
- [ ] Code coverage ≥70%
- [ ] Linting passes
- [ ] Type hints added
- [ ] Documentation updated
- [ ] Health checks passing
- [ ] No hardcoded secrets

---

## Additional Resources

### Documentation

- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc
- **Project Report**: See `REPORT.md` for detailed DevOps implementation

### Project Structure

```
D-D-Initiative/
├── backend/              # Python FastAPI backend
│   ├── app/
│   │   ├── routers/     # API endpoints
│   │   ├── models/      # Database models
│   │   └── utils/       # Utilities (auth, metrics)
│   ├── tests/           # Test suite
│   └── pytest.ini       # Test configuration
├── frontend/            # Node.js frontend
├── monitoring/          # Prometheus & Grafana configs
├── .github/workflows/   # CI/CD pipelines
└── docker-compose.yml   # Container orchestration
```

### Support

For issues or questions:
1. Check this documentation
2. Review `REPORT.md` for implementation details
3. Check GitHub Issues
4. Review CI/CD pipeline logs

---

**Last Updated**: November 17, 2025  
**Version**: 1.0.0

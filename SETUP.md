# 🚀 Setup Guide for D&D Initiative Tracker

This guide will help you clone and run this project on your local machine or deploy it to production.

## 📋 Prerequisites

Before starting, ensure you have the following installed:

- **Docker Desktop** (version 20.10 or higher) - [Download](https://www.docker.com/products/docker-desktop/)
- **Git** - [Download](https://git-scm.com/downloads)
- **Optional**: Node.js 18+ and Python 3.11+ for local development without Docker

## 🎯 Quick Start (Recommended)

### 1. Clone the Repository

```bash
git clone https://github.com/L96Expanded/D-D-Initiative.git
cd D-D-Initiative
```

### 2. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and update these REQUIRED values:
# - POSTGRES_PASSWORD: Choose a strong password
# - JWT_SECRET: Generate a random 32+ character string
# - SECRET_KEY: Same as JWT_SECRET
```

**🔒 Security Note**: NEVER commit your `.env` file! It's already in `.gitignore`.

#### Generating Secure Secrets

**Windows PowerShell:**
```powershell
# Generate a random JWT secret
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
```

**Linux/Mac:**
```bash
# Generate a random JWT secret
openssl rand -base64 32
```

### 3. Start the Application

```bash
# Start all services with Docker Compose
docker-compose up -d

# View logs to ensure everything started correctly
docker-compose logs -f
```

Wait for all services to become healthy (usually 30-60 seconds). You should see:
```
✔ Container dnd_postgres   Healthy
✔ Container dnd_backend    Started  
✔ Container dnd_frontend   Started
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

### 5. Create Your First Account

1. Open http://localhost:3000
2. Click "Register"
3. Create your account
4. Start tracking encounters!

## 🛠️ Development Setup (Without Docker)

If you prefer to run services individually for development:

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set environment variables
export DATABASE_URL="postgresql://dnd_user:your_password@localhost:5432/dnd_tracker"
export JWT_SECRET="your_secret_key"

# Run database migrations (if applicable)
# alembic upgrade head

# Start the backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy frontend environment file
cp .env.example .env.local

# Edit .env.local and set VITE_API_URL
# VITE_API_URL=http://localhost:8000

# Start development server
npm run dev
```

### Database Setup

You still need PostgreSQL running. Use Docker for just the database:

```bash
docker run -d \
  --name dnd_postgres \
  -e POSTGRES_DB=dnd_tracker \
  -e POSTGRES_USER=dnd_user \
  -e POSTGRES_PASSWORD=your_password \
  -p 5432:5432 \
  postgres:15
```

## 🧪 Running Tests

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html --cov-report=term-missing

# Run specific test file
pytest tests/test_auth.py -v

# Open coverage report
# Windows:
start htmlcov/index.html
# Linux:
xdg-open htmlcov/index.html
# Mac:
open htmlcov/index.html
```

### Frontend Tests

```bash
cd frontend

# Run tests (if configured)
npm test

# Run linter
npm run lint
```

## 📦 Building for Production

### Using Docker

```bash
# Build production images
docker-compose -f docker-compose.yml build

# Start in production mode
docker-compose -f docker-compose.yml up -d
```

### Manual Build

**Backend:**
```bash
cd backend
pip install -r requirements.txt
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

**Frontend:**
```bash
cd frontend
npm run build
# Serve the dist/ folder with nginx or any static file server
```

## 🐛 Troubleshooting

### Port Already in Use

If you get "port already in use" errors:

```bash
# Stop all Docker containers
docker-compose down

# Check what's using the ports (Windows)
netstat -ano | findstr :3000
netstat -ano | findstr :8000
netstat -ano | findstr :5432

# Check what's using the ports (Linux/Mac)
lsof -i :3000
lsof -i :8000
lsof -i :5432

# Kill the process or change ports in docker-compose.yml
```

### Database Connection Issues

```bash
# Check if PostgreSQL container is running
docker ps

# View PostgreSQL logs
docker-compose logs postgres

# Reset the database
docker-compose down -v
docker-compose up -d
```

### Backend Won't Start

```bash
# View backend logs
docker-compose logs backend

# Rebuild backend image
docker-compose build backend
docker-compose up -d backend

# Check environment variables are set correctly
docker-compose exec backend env | grep -E 'DATABASE_URL|JWT_SECRET'
```

### Frontend Can't Connect to Backend

1. Verify backend is running: http://localhost:8000/api/health
2. Check frontend environment variable:
   ```bash
   # In frontend/.env.local (for local dev)
   VITE_API_URL=http://localhost:8000
   ```
3. Check CORS settings in backend `config.py`

### Permission Denied Errors

```bash
# Linux/Mac: Fix permissions for uploads directory
sudo chown -R $USER:$USER uploads/

# Or run Docker with proper permissions
docker-compose up --build --force-recreate
```

## 🔄 Updating the Application

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart containers
docker-compose down
docker-compose up --build -d

# View logs to ensure update was successful
docker-compose logs -f
```

## 🗄️ Backup and Restore

### Backup Database

```bash
# Create backup
docker-compose exec postgres pg_dump -U dnd_user dnd_tracker > backup_$(date +%Y%m%d_%H%M%S).sql

# Or use Docker volume backup
docker run --rm \
  -v dnd-initiative_postgres_data:/data \
  -v $(pwd):/backup \
  ubuntu tar czf /backup/db_backup.tar.gz /data
```

### Restore Database

```bash
# Restore from SQL dump
docker-compose exec -T postgres psql -U dnd_user dnd_tracker < backup.sql

# Or restore volume
docker run --rm \
  -v dnd-initiative_postgres_data:/data \
  -v $(pwd):/backup \
  ubuntu bash -c "cd /data && tar xzf /backup/db_backup.tar.gz --strip 1"
```

## 🌐 Deploying to Cloud

See the main README.md for detailed Azure deployment instructions. The application is already configured for:

- **Azure Static Web Apps** (Frontend)
- **Azure App Service** (Backend)
- **Azure Database for PostgreSQL** (Database)

GitHub Actions workflows are included for CI/CD automation.

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/docs (when running)
- **Database Schema**: See `backend/app/models/models.py`
- **Frontend Components**: See `frontend/src/components/`
- **Test Files**: See `backend/tests/`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `pytest` and `npm test`
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push to branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

## ❓ Getting Help

If you encounter issues:

1. Check this setup guide thoroughly
2. Review the troubleshooting section
3. Check existing GitHub Issues
4. Create a new issue with:
   - Your operating system
   - Docker version (`docker --version`)
   - Error messages and logs
   - Steps to reproduce

## 📄 License

This project is provided as-is for educational purposes.

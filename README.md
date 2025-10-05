# 🎲 D&D Initiative Tracker

A modern, full-stack web application for tracking D&D encounters with a beautiful glassmorphism design. Built with React, FastAPI, and PostgreSQL.

## ✨ Features

- **User Authentication**: Secure JWT-based authentication with registration and login
- **Encounter Management**: Create, edit, and delete encounters with multiple creatures
- **Initiative Tracking**: Automatic sorting by initiative with turn-by-turn progression
- **File Upload**: Image support for creatures and encounter backgrounds
- **Responsive Design**: Modern glassmorphism UI that works on all devices
- **Real-time Updates**: Dynamic encounter state management

## 🛠️ Tech Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for fast development and building
- **React Router** for navigation
- **Axios** for API communication
- **CSS3** with glassmorphism design

### Backend
- **FastAPI** with Python 3.11
- **SQLAlchemy 2.0** with async support
- **PostgreSQL 15** database
- **JWT** authentication with bcrypt
- **Pydantic** for data validation

### Infrastructure
- **Docker & Docker Compose** for containerization
- **Nginx** for frontend serving
- **Volume mounting** for data persistence

## 🚀 Quick Setup

### Prerequisites
- **Docker Desktop** - [Download here](https://www.docker.com/products/docker-desktop/)
- **Git** - [Download here](https://git-scm.com/downloads)

### Installation

1. **Clone and Start**
   ```bash
   git clone https://github.com/L96Expanded/D-D-Initiative.git
   cd D-D-Initiative
   docker-compose up --build
   ```

2. **Access the Application**
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs

3. **First Use**
   - Register a new account at http://localhost:3000
   - Create encounters and start tracking initiative!

### Stop the Application
```bash
docker-compose down
```

### Basic Troubleshooting

**Port Conflicts:**
- Ensure ports 3000, 8000, and 5432 are available
- Change ports in `docker-compose.yml` if needed

**Reset Everything:**
```bash
docker-compose down -v
docker-compose up --build
```

**View Logs:**
```bash
docker-compose logs backend
docker-compose logs frontend
```

## 📁 Project Structure

```
D-D-Initiative/
├── docker-compose.yml          # Docker services configuration
├── .env                        # Environment variables
├── README.md                   # This file
├── frontend/                   # React frontend application
│   ├── src/
│   │   ├── pages/             # Page components (Login, Register, Home, Encounter)
│   │   ├── components/        # Reusable UI components
│   │   ├── context/           # React Context providers
│   │   ├── utils/             # Utility functions and API client
│   │   ├── types/             # TypeScript type definitions
│   │   └── styles/            # CSS files with glassmorphism design
│   ├── public/
│   │   └── images/            # Static images and assets
│   ├── Dockerfile             # Frontend container configuration
│   ├── package.json           # Frontend dependencies
│   └── vite.config.ts         # Vite configuration
├── backend/                    # FastAPI backend application
│   ├── app/
│   │   ├── models/            # SQLAlchemy models and Pydantic schemas
│   │   ├── routers/           # API route handlers
│   │   ├── utils/             # Authentication and utility functions
│   │   └── config.py          # Application configuration
│   ├── Dockerfile             # Backend container configuration
│   ├── requirements.txt       # Python dependencies
│   └── main.py               # FastAPI application entry point
└── uploads/                   # Volume for uploaded files
```

## 🚀 Getting Started

1. **Start the application**: `docker-compose up --build`
2. **Access the frontend**: http://localhost:3000
3. **Create an account** and start tracking your encounters!

For detailed instructions, API documentation, and troubleshooting, see the full documentation in the project files.

Happy adventuring! 🗡️✨

---

## 🧪 Testing

The project includes a comprehensive testing framework with 102 test cases covering authentication, creature management, and encounter functionality.

### Current Test Status
- **Total Tests**: 148 test cases (was 102)
- **Passing Tests**: 146 (98.6%) 
- **Code Coverage**: **99%** (was 82%)

### Test Suites
- ✅ **Authentication Tests**: 28/28 passing (100%)
- ✅ **Creature Management Tests**: 41/43 passing (95.3%)  
- ✅ **Encounter Tests**: 24/24 passing (100%)*
- ✅ **Standalone Creature Tests**: 19/19 passing (100%)
- ✅ **Upload Tests**: 24/24 passing (100%)
- ✅ **User Profile Tests**: 15/15 passing (100%)
- ✅ **Database Tests**: 10/10 passing (100%)
- 🔄 **7 Tests Skipped**: Initiative management endpoints (planned for future implementation)

*All currently implemented encounter functionality is fully tested

### Running Tests
```bash
# Navigate to backend directory
cd backend

# Run all tests with coverage
python -m pytest tests/ --cov=app --cov-report=term-missing

# Run specific test suite
python -m pytest tests/test_auth.py -v
python -m pytest tests/test_creatures.py -v
python -m pytest tests/test_encounters.py -v

# Generate HTML coverage report
python -m pytest tests/ --cov=app --cov-report=html:htmlcov
```

For detailed testing documentation, see [docs/TESTING.md](docs/TESTING.md).

---
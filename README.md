# 🎲 D&D Initiative Tracker

A modern, full-stack web application for tracking D&D encounters with a beautiful glassmorphism design. Built with React, FastAPI, and PostgreSQL.

## ✨ Features

- **User Authentication**: Secure JWT-based authentication with registration and login
- **Dual-Window System**: Separate DM control panel and player display window
- **Encounter Management**: Create, edit, and delete encounters with multiple creatures
- **Initiative Tracking**: Automatic sorting by initiative with turn-by-turn progression
- **Real-time Sync**: Display window updates automatically when DM makes changes
- **File Upload**: Image support for creatures and encounter backgrounds
- **Responsive Design**: Modern glassmorphism UI that works on all devices
- **One-Click Launcher**: Desktop shortcut to automatically start everything

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

### One-Click Launcher (Recommended)
1. **Double-click** `create-shortcut.bat` to create a desktop shortcut
2. **Double-click** the "DnD Initiative Tracker" shortcut on your desktop
3. The script will automatically:
   - Start Docker Desktop if needed
   - Build and run the application
   - Open your browser to http://localhost:3000
4. Start your D&D session! 🎲

## 🏁 Complete Setup Guide (From Scratch)

**New to this? No problem!** This guide will take you from zero to running the D&D Initiative Tracker, even if you only have GitHub and VS Code installed.

### Step 1: Install Required Software

#### 1.1 Install Docker Desktop
Docker is required to run the application containers.
1. **Download Docker Desktop**: https://www.docker.com/products/docker-desktop/
2. **Run the installer** and follow the setup wizard
3. **Restart your computer** when prompted
4. **Start Docker Desktop** from your Start menu
5. **Wait for Docker to fully start** (you'll see a green icon in the system tray)

#### 1.2 Install Git (if not already installed)
Git is needed to download the project code.
1. **Download Git**: https://git-scm.com/downloads
2. **Run the installer** with default settings
3. **Verify installation**: Open Command Prompt and type `git --version`

### Step 2: Download and Start the Application

#### 2.1 Clone the Project
1. **Open Command Prompt or PowerShell**
2. **Navigate to your desired folder** (e.g., `cd Desktop`)
3. **Clone the repository**:
   ```bash
   git clone https://github.com/L96Expanded/D-D-Initiative.git
   ```
4. **Enter the project folder**:
   ```bash
   cd D-D-Initiative
   ```

#### 2.2 Start the Application
1. **Make sure Docker Desktop is running** (green whale icon in system tray)
2. **Build and start the application**:
   ```bash
   docker-compose up --build
   ```
3. **Wait for the build to complete** (this may take 5-10 minutes the first time)
4. **Look for these success messages**:
   ```
   ✔ Container dnd_postgres   Healthy
   ✔ Container dnd_backend    Started  
   ✔ Container dnd_frontend   Started
   ```
5. **Open your browser** to http://localhost:3000
6. **Create your first account** and start using the tracker!

#### 2.3 Stop the Application (When Done)
- **Press `Ctrl+C`** in the Command Prompt to stop
- Or run: `docker-compose down`

### Step 3: Create Desktop Shortcut (Optional but Recommended)

#### 3.1 Windows Desktop Shortcut
1. **Navigate to your project folder** in File Explorer
2. **Double-click** `create-shortcut.bat` 
3. **A "DnD Initiative Tracker" shortcut** will appear on your desktop
4. **Future use**: Just double-click the desktop shortcut to start everything automatically!

#### 3.2 Manual Shortcut (Alternative)
If the batch file doesn't work:
1. **Right-click on Desktop** → New → Shortcut
2. **Location**: `cmd /c "cd /d C:\path\to\D-D-Initiative && docker-compose up"`
   - Replace `C:\path\to\D-D-Initiative` with your actual folder path
3. **Name**: "DnD Initiative Tracker"
4. **Right-click the shortcut** → Properties → Change Icon (optional)

### Step 4: Add Chrome Extension (Optional - Enhanced Experience)

The Chrome extension provides additional features for DMs running encounters.

#### 4.1 Install the Extension
1. **Open Google Chrome**
2. **Navigate to your project folder** → `chrome-extension` folder
3. **Open Chrome Extensions page**: 
   - Type `chrome://extensions/` in the address bar, or
   - Menu (⋮) → More Tools → Extensions
4. **Enable Developer Mode** (toggle in top-right corner)
5. **Click "Load unpacked"**
6. **Select the `chrome-extension` folder** from your project
7. **Pin the extension** (puzzle piece icon → pin the D&D Initiative Tracker)

#### 4.2 Using the Extension
1. **Start your web application** (http://localhost:3000)
2. **Login to your account**
3. **Click the extension icon** in Chrome toolbar
4. **Additional DM tools** will be available while managing encounters

### Step 5: First Time Usage

#### 5.1 Create Your Account
1. **Go to** http://localhost:3000
2. **Click "Register"**
3. **Fill in your details** and create an account
4. **Login with your new credentials**

#### 5.2 Create Your First Encounter
1. **Click "Create New Encounter"**
2. **Add encounter details** (name, description)
3. **Add creatures** with initiative values
4. **Start the encounter** and begin tracking!

#### 5.3 Use the Dual-Window System
1. **Main Window**: Your DM control panel (http://localhost:3000)
2. **Display Window**: Player-facing display (click "Open Display Window")
3. **Share the display window** on a second monitor or TV for players to see

## 🛠️ Troubleshooting

### Common Issues

**"Port already in use" error:**
- Something else is using ports 3000, 8000, or 5432
- Close other applications or change ports in `docker-compose.yml`

**Docker Desktop not starting:**
- Restart Docker Desktop
- Restart your computer
- Check Windows/Mac system requirements

**Browser can't connect:**
- Wait a few more minutes for containers to fully start
- Check Docker Desktop shows all containers as "Running"
- Try refreshing the page

**Reset everything:**
```bash
docker-compose down -v
docker-compose up --build
```

### Manual Setup
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
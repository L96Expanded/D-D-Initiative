# 🎲 D&D Initiative Tracker

A modern, full-stack web application for tracking D&D encounters with worldwide access and automated CI/CD deployment. Built with React, FastAPI, PostgreSQL, and Azure Static Web Apps.

## 🚀 **ONE-CLICK STARTUP**

**Start everything with a single click!**

```bash
# Double-click to start EVERYTHING:
START_EVERYTHING.bat
```

**What it does automatically:**
- ✅ Builds and starts Docker containers
- ✅ Starts Cloudflare tunnel for worldwide access  
- ✅ Opens application in browser
- ✅ Makes your D&D tracker accessible at: **https://karsusinitiative.com**

**Perfect for DMs who move between locations!** 🏠➡️🏢➡️🎮

## ✨ Features

- **🌐 Worldwide Access**: Host from anywhere, players access from anywhere via https://karsusinitiative.com
- **👤 User Authentication**: Secure JWT-based authentication with registration and login
- **🪟 Dual-Window System**: Separate DM control panel and player display window
- **⚔️ Encounter Management**: Create, edit, and delete encounters with multiple creatures
- **🎯 Initiative Tracking**: Automatic sorting by initiative with turn-by-turn progression
- **🔄 Real-time Sync**: Display window updates automatically when DM makes changes
- **📁 File Upload**: Image support for creatures and encounter backgrounds
- **📱 Mobile-Friendly**: Works perfectly on phones, tablets, and computers
- **🖱️ One-Click Everything**: Desktop shortcut to automatically start everything
- **🔐 Production Security**: JWT authentication, CORS protection, secure tunneling

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

### ⚡ Fastest Way: Automated Setup Script

Just clone and run the setup script - it handles everything!

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

**What it does automatically:**
- ✅ Checks Docker is installed and running
- ✅ Creates `.env` file with secure passwords  
- ✅ Builds and starts all Docker containers
- ✅ Waits for services to be ready
- ✅ Opens the app in your browser

**See [QUICKSTART.md](QUICKSTART.md) for detailed setup instructions!**

## 📖 Manual Setup

If the automated script doesn't work or you prefer manual setup:

### Prerequisites
- **Docker Desktop** - [Download here](https://www.docker.com/products/docker-desktop/)
- **Git** - [Download here](https://git-scm.com/downloads)

### Installation Steps

```bash
# 1. Clone the repository
git clone https://github.com/L96Expanded/D-D-Initiative.git
cd D-D-Initiative

# 2. Create environment file
cp .env.example .env
# Edit .env and change POSTGRES_PASSWORD and JWT_SECRET to secure values

# 3. Build and start containers
docker-compose up --build -d

# 4. Wait 30-60 seconds for services to start

# 5. Open your browser to http://localhost:3000
```

### First Time Usage

1. **Create Account**: Register at http://localhost:3000
2. **Create Encounter**: Click "Create New Encounter"
3. **Add Creatures**: Add creatures with initiative values
4. **Start Tracking**: Click "Start Encounter" and use "Next Turn"

### Stop the Application
```bash
docker-compose down
```

## 🛠️ Troubleshooting

### Common Issues

**"Port already in use" error:**
```bash
# Stop conflicting services or change ports in docker-compose.yml
# Default ports: 3000 (frontend), 8000 (backend), 5432 (database)
```

**Docker not running:**
- Ensure Docker Desktop is running (green whale icon in system tray)
- Wait a full minute after starting Docker before running commands

**Cannot connect to application:**
```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs backend
docker-compose logs frontend

# Wait longer - first build can take 5-10 minutes
```

**Reset everything:**
```bash
docker-compose down -v  # Removes all data!
docker-compose up --build -d
```

### Access URLs

Once running:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

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

## 🌐 Internet Access Setup (Advanced)

**Want to allow friends to join from anywhere on the internet?** Follow this guide to make your D&D Initiative Tracker accessible from other devices and locations.

### ⚠️ Security Warning
Making your application internet-accessible requires proper security measures. Only proceed if you understand the risks and responsibilities involved.

### Prerequisites for Internet Access
- **Router admin access** (to configure port forwarding)
- **Static IP or Dynamic DNS service** (like No-IP, DuckDNS)
- **Domain name** (optional but recommended)
- **SSL certificate** (highly recommended for security)

### Step 1: Configure Production Environment

1. **Copy the production environment file**:
   ```bash
   copy .env.production .env.prod
   ```

2. **Edit `.env.prod`** and update these critical values:
   ```env
   # Change these BEFORE deployment!
   POSTGRES_PASSWORD=your_very_secure_database_password_here
   JWT_SECRET=your_very_long_random_jwt_secret_key_here
   DOMAIN_NAME=your-domain.com  # or your external IP
   ```

3. **Generate secure secrets**:
   - **Database Password**: Use a password manager to generate a strong password
   - **JWT Secret**: Generate a long random string (minimum 64 characters)

### Step 2: Deploy in Production Mode

**Windows:**
```bash
.\deploy-production.bat
```

**Linux/Mac:**
```bash
chmod +x deploy-production.sh
./deploy-production.sh
```

### Step 3: Configure Your Router

1. **Access your router's admin panel** (usually http://192.168.1.1)
2. **Find "Port Forwarding" or "Virtual Server"** section
3. **Add these forwarding rules**:
   - **Port 80** → Your computer's local IP (192.168.x.x)
   - **Port 8000** → Your computer's local IP (192.168.x.x)
   - **Port 443** → Your computer's local IP (192.168.x.x) (for HTTPS)

### Step 4: Set Up Dynamic DNS (Recommended)

If you don't have a static IP address:

1. **Sign up for a free Dynamic DNS service**:
   - [No-IP](https://www.noip.com) (free)
   - [DuckDNS](https://www.duckdns.org) (free)
   - [Dynu](https://www.dynu.com) (free)

2. **Create a hostname** (e.g., `mydndgame.ddns.net`)
3. **Update your `.env.prod`** with your hostname:
   ```env
   DOMAIN_NAME=mydndgame.ddns.net
   ```

### Step 5: Share Access with Players

Once configured, players can access your game at:
- **Main App**: `http://your-domain.com` or `http://your-external-ip`
- **Display Window**: They can open the display window from within the app

### Step 6: Security Best Practices

1. **Use HTTPS** (SSL certificates):
   - Get free SSL from [Let's Encrypt](https://letsencrypt.org)
   - Update nginx configuration to enable SSL

2. **Regular backups**:
   ```bash
   # Backup your data
   docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U dnd_user dnd_tracker > backup.sql
   ```

3. **Monitor access logs**:
   ```bash
   docker-compose -f docker-compose.prod.yml logs backend
   ```

4. **Update regularly**:
   ```bash
   git pull
   .\deploy-production.bat
   ```

### Troubleshooting Internet Access

**Can't connect from outside:**
- Check router port forwarding is correct
- Verify your external IP hasn't changed
- Test with your phone's mobile data (not WiFi)

**Security concerns:**
- Use strong passwords for all accounts
- Enable two-factor authentication if possible
- Consider using a VPN for sensitive sessions

**Performance issues:**
- Check your internet upload speed
- Consider upgrading your hosting if many users

### Alternative: Cloud Hosting

For easier internet access, consider deploying to cloud platforms:
- **DigitalOcean** ($5/month droplet)
- **AWS EC2** (free tier available)
- **Google Cloud Platform** (free tier available)
- **Microsoft Azure** (free tier available)

---

## 🧪 Testing

The project includes a comprehensive testing framework with 102 test cases covering authentication, creature management, and encounter functionality.

### Current Test Status
- **Total Tests**: 148 test cases (was 102)
- **Passing Tests**: 146 (98.6%) 
- **Code Coverage**: **99%** (was 82%)

### Test Suites
-  **Authentication Tests**: 28/28 passing (100%)
-  **Creature Management Tests**: 41/43 passing (95.3%)  
-  **Encounter Tests**: 24/24 passing (100%)*
-  **Standalone Creature Tests**: 19/19 passing (100%)
-  **Upload Tests**: 24/24 passing (100%)
-  **User Profile Tests**: 15/15 passing (100%)
-  **Database Tests**: 10/10 passing (100%)
-  **7 Tests Skipped**: Initiative management endpoints (planned for future implementation)

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

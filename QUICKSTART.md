# 🚀 QUICKSTART GUIDE - D&D Initiative Tracker

**Get up and running in 5 minutes!** This guide will help you clone the repo and set everything up, even if you're new to Docker.

---

## 📋 Prerequisites

You only need **TWO things** installed:

### 1️⃣ Git
Already have it? Skip to step 2.
- **Windows**: Download from [git-scm.com](https://git-scm.com/downloads)
- **Mac**: Install via Homebrew: `brew install git` or download from [git-scm.com](https://git-scm.com/downloads)
- **Linux**: `sudo apt install git` (Ubuntu/Debian) or `sudo yum install git` (CentOS/RHEL)

### 2️⃣ Docker Desktop
- **Download**: [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)
- **Install** and **restart** your computer
- **Start Docker Desktop** (wait for green icon in system tray)

**That's it! No Python, Node.js, PostgreSQL, or other dependencies needed!** Docker handles everything.

---

## ⚡ 3-Step Setup (Automated)

### Option A: Automated Setup (Recommended)

#### **Windows Users:**

```powershell
# 1. Clone the repository
git clone https://github.com/L96Expanded/D-D-Initiative.git
cd D-D-Initiative

# 2. Run the automated setup script
powershell -ExecutionPolicy Bypass -File setup.ps1

# That's it! The script does everything automatically:
#   ✅ Checks Docker is installed and running
#   ✅ Creates .env file with secure passwords
#   ✅ Builds and starts all containers
#   ✅ Waits for services to be ready
#   ✅ Opens the app in your browser
```

#### **Mac/Linux Users:**

```bash
# 1. Clone the repository
git clone https://github.com/L96Expanded/D-D-Initiative.git
cd D-D-Initiative

# 2. Make the setup script executable
chmod +x setup.sh

# 3. Run the automated setup
./setup.sh

# That's it! The script does everything automatically:
#   ✅ Checks Docker is installed and running
#   ✅ Creates .env file with secure passwords
#   ✅ Builds and starts all containers
#   ✅ Waits for services to be ready
#   ✅ Opens the app in your browser
```

---

### Option B: Manual Setup

If you prefer to do it manually or the script doesn't work:

```bash
# 1. Clone the repository
git clone https://github.com/L96Expanded/D-D-Initiative.git
cd D-D-Initiative

# 2. Create environment configuration
cp .env.example .env
# Edit .env and change POSTGRES_PASSWORD and JWT_SECRET to secure values

# 3. Build and start Docker containers
docker-compose up --build -d

# 4. Wait 30-60 seconds for containers to fully start

# 5. Open your browser
# Go to: http://localhost:3000
```

---

## 🎮 Your Application is Running!

Once setup is complete, access the application:

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Main application interface |
| **Backend API** | http://localhost:8000 | REST API |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Health Check** | http://localhost:8000/api/health | Service health status |

---

## 🎯 First Time Usage

### 1. Create Your Account
1. Open http://localhost:3000
2. Click **"Register"**
3. Fill in username, email, and password
4. Click **"Sign Up"**

### 2. Create Your First Encounter
1. After logging in, click **"Create New Encounter"**
2. Enter encounter details:
   - **Name**: e.g., "Goblin Ambush"
   - **Description**: e.g., "Party encounters goblins on the road"
3. Click **"Create"**

### 3. Add Creatures
1. In your encounter, click **"Add Creature"**
2. Fill in details:
   - **Name**: e.g., "Goblin Archer"
   - **Initiative**: 14
   - **Type**: Enemy
   - **Image** (optional): Upload or auto-fetch
3. Repeat to add more creatures and player characters

### 4. Start Tracking Initiative
1. Click **"Start Encounter"**
2. Creatures automatically sort by initiative
3. Use **"Next Turn"** to advance through rounds
4. Click **"Open Display Window"** for a player-facing view

---

## 🛠️ Common Commands

```bash
# View container status
docker-compose ps

# View live logs (all services)
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop the application
docker-compose down

# Stop and remove all data (fresh start)
docker-compose down -v

# Restart services
docker-compose restart

# Rebuild containers after code changes
docker-compose up --build -d
```

---

## 🐛 Troubleshooting

### Problem: "Port already in use"
**Solution**: Another application is using ports 3000, 8000, or 5432
```bash
# Find and stop the conflicting process
# Windows:
netstat -ano | findstr :3000
netstat -ano | findstr :8000

# Mac/Linux:
lsof -i :3000
lsof -i :8000

# Or change ports in docker-compose.yml
```

### Problem: "Cannot connect" or containers not starting
**Solution**: 
1. Ensure Docker Desktop is running (green whale icon)
2. Wait a full minute after `docker-compose up`
3. Check container health: `docker-compose ps`
4. View logs: `docker-compose logs backend`

### Problem: Database connection errors
**Solution**: 
```bash
# Reset everything and start fresh
docker-compose down -v
docker-compose up --build -d
```

### Problem: Frontend can't connect to backend
**Solution**:
1. Verify backend is running: `curl http://localhost:8000/api/health`
2. Check VITE_API_URL in .env is set to `http://localhost:8000`
3. Rebuild frontend: `docker-compose up --build -d frontend`

### Problem: Permission denied (Linux/Mac)
**Solution**:
```bash
# Make setup script executable
chmod +x setup.sh

# Fix Docker permissions
sudo usermod -aG docker $USER
# Then log out and log back in
```

---

## 📝 Environment Variables

The `.env` file contains all configuration. **Important variables**:

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_PASSWORD` | changeme | **⚠️ MUST CHANGE!** Database password |
| `JWT_SECRET` | changeme | **⚠️ MUST CHANGE!** Authentication secret (64+ chars) |
| `ENVIRONMENT` | development | `development` or `production` |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed frontend origins |
| `VITE_API_URL` | `http://localhost:8000` | Backend API URL for frontend |

**Security Tip**: Generate secure secrets with:
```bash
# Python method
python -c "import secrets; print(secrets.token_urlsafe(64))"

# OpenSSL method
openssl rand -base64 64
```

---

## 🌐 Accessing from Other Devices

### Same Network (e.g., show players on tablets)

1. Find your computer's local IP:
   ```bash
   # Windows
   ipconfig
   # Look for "IPv4 Address" (e.g., 192.168.1.100)
   
   # Mac/Linux
   ifconfig | grep "inet "
   # or
   ip addr show
   ```

2. Update `.env` file:
   ```env
   CORS_ORIGINS=["http://localhost:3000","http://192.168.1.100:3000"]
   ALLOWED_HOSTS=["localhost","127.0.0.1","192.168.1.100"]
   ```

3. Restart containers:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

4. Players access: `http://192.168.1.100:3000` (use YOUR IP)

---

## 🚀 Next Steps

- **Read the full README**: [README.md](README.md) for detailed features
- **Deploy to Production**: See [SETUP.md](SETUP.md) for cloud deployment
- **API Documentation**: Visit http://localhost:8000/docs
- **Customize**: See [docker-compose.yml](docker-compose.yml) to modify ports or add services
- **Backup Data**: See [scripts/backup-database.bat](scripts/backup-database.bat)

---

## 💡 Tips for Best Experience

1. **Use Chrome or Firefox** for best compatibility
2. **Enable Pop-ups** to use the Display Window feature
3. **Keep Docker Desktop running** while using the application
4. **Regular backups**: The database is in a Docker volume (persistent)
5. **Updates**: `git pull && docker-compose up --build -d` to get latest changes

---

## 🎲 Ready to Play!

You're all set! Create encounters, track initiative, and enjoy your D&D sessions!

**Need help?** Check the [README.md](README.md) or open an issue on GitHub.

**Happy Adventuring!** 🗡️✨

---

## 📞 Support

- **Documentation**: [README.md](README.md) | [SETUP.md](SETUP.md)
- **GitHub Issues**: [github.com/L96Expanded/D-D-Initiative/issues](https://github.com/L96Expanded/D-D-Initiative/issues)
- **API Docs**: http://localhost:8000/docs (when running)

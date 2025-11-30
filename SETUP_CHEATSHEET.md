# 🚀 SETUP CHEAT SHEET

## For Users Who Just Want to Run the App

### Windows
```powershell
git clone https://github.com/L96Expanded/D-D-Initiative.git
cd D-D-Initiative
powershell -ExecutionPolicy Bypass -File setup.ps1
```

### Mac/Linux
```bash
git clone https://github.com/L96Expanded/D-D-Initiative.git
cd D-D-Initiative
chmod +x setup.sh
./setup.sh
```

**That's it!** Script does everything automatically.

---

## Useful Commands After Setup

```bash
# Start the application
docker-compose up -d

# Stop the application
docker-compose down

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Check status
docker-compose ps

# Complete reset (deletes data!)
docker-compose down -v
docker-compose up --build -d
```

---

## Access URLs

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health:** http://localhost:8000/api/health

---

## Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Port in use | Change ports in `docker-compose.yml` |
| Can't connect | Wait 1-2 minutes, check `docker-compose ps` |
| Docker not running | Start Docker Desktop, wait for green icon |
| Need fresh start | `docker-compose down -v && docker-compose up --build` |

---

## File Structure Basics

```
D-D-Initiative/
├── frontend/           # React app
├── backend/            # FastAPI app
├── .env               # Your config (DO NOT COMMIT!)
├── .env.example       # Template for .env
├── docker-compose.yml # Docker configuration
├── setup.ps1          # Windows setup script
├── setup.sh           # Mac/Linux setup script
├── QUICKSTART.md      # Detailed setup guide
└── README.md          # Full documentation
```

---

## Need More Help?

- **Quick Setup:** [QUICKSTART.md](QUICKSTART.md)
- **Full Docs:** [README.md](README.md)
- **Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md)
- **Issues:** [GitHub Issues](https://github.com/L96Expanded/D-D-Initiative/issues)

---

## Security Notes

- Never commit `.env` file
- Change `POSTGRES_PASSWORD` and `JWT_SECRET` in `.env`
- For production, set `ENVIRONMENT=production` in `.env`

---

**Happy D&D-ing!** 🎲✨

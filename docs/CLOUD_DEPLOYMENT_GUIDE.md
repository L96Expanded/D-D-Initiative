# Cloud Deployment Guide for Mobile D&D Initiative Tracker

## 🌟 **Why Cloud Hosting?**

For someone moving between locations, cloud hosting is the ideal solution:
- ✅ **No router configuration needed**
- ✅ **Works from any internet connection**
- ✅ **Professional static IP addresses**
- ✅ **24/7 availability**
- ✅ **Backup and scaling options**

## 🚀 **Recommended Cloud Services**

### **Option 1: DigitalOcean (Recommended)**
**Cost:** ~$6-12/month
**Why:** Docker-friendly, simple setup, great for beginners

**Setup Steps:**
1. Create DigitalOcean account
2. Deploy Docker Droplet (Ubuntu)
3. Upload your project files
4. Run your deployment scripts
5. Point Cloudflare to droplet IP

### **Option 2: AWS Lightsail**
**Cost:** ~$5-10/month
**Why:** Part of AWS ecosystem, reliable

### **Option 3: Linode**
**Cost:** ~$5-10/month
**Why:** Developer-friendly, excellent documentation

### **Option 4: Google Cloud Platform**
**Cost:** ~$5-15/month (may have free tier)
**Why:** Powerful, scalable

## 🔧 **Cloud Deployment Process**

### Step 1: Choose and Set Up Cloud Server

**DigitalOcean Example:**
1. Create account at digitalocean.com
2. Create new Droplet:
   - **Image:** Ubuntu 22.04 LTS
   - **Size:** Basic $6/month (1GB RAM, 1 vCPU)
   - **Region:** Choose closest to your locations
   - **Authentication:** SSH Key (recommended)

### Step 2: Prepare Your Server

SSH into your server:
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose -y

# Create project directory
mkdir ~/dnd-initiative
cd ~/dnd-initiative
```

### Step 3: Upload Your Project

**Method 1: Git (Recommended)**
```bash
# Clone your repository
git clone https://github.com/L96Expanded/D-D-Initiative.git
cd D-D-Initiative
```

**Method 2: SCP Upload**
```bash
# From your local machine
scp -r C:\Users\david\Desktop\School\DevOps\DnD_Initiative_Project\D-D-Initiative root@[server-ip]:~/
```

### Step 4: Deploy on Cloud Server

```bash
# Make scripts executable
chmod +x *.sh *.bat

# Create environment file
cp .env.production .env

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

### Step 5: Configure Cloudflare

1. Go to Cloudflare DNS settings
2. Update A records:
   - `@` → `[your-cloud-server-ip]`
   - `www` → `[your-cloud-server-ip]`
   - `api` → `[your-cloud-server-ip]`

## 🔄 **Development Workflow**

### Local Development
1. Work on your laptop as usual
2. Test locally with `docker-compose up`
3. Commit changes to Git

### Cloud Deployment
```bash
# SSH to cloud server
ssh root@[server-ip]

# Update code
cd ~/D-D-Initiative
git pull origin main

# Redeploy
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build
```

### Automated Deployment (Advanced)
Set up GitHub Actions for automatic deployment:
- Push to main branch
- Automatically deploys to cloud server
- Zero-downtime updates

## 💰 **Cost Comparison**

| Service | Monthly Cost | RAM | CPU | Storage | Bandwidth |
|---------|-------------|-----|-----|---------|-----------|
| DigitalOcean | $6 | 1GB | 1 vCPU | 25GB | 1TB |
| AWS Lightsail | $5 | 1GB | 1 vCPU | 20GB | 1TB |
| Linode | $5 | 1GB | 1 vCPU | 25GB | 1TB |
| Google Cloud | $5-15 | 1GB | 1 vCPU | 10GB | Various |

## 🛡️ **Security for Cloud Hosting**

### Server Security
```bash
# Create non-root user
sudo adduser dnduser
sudo usermod -aG sudo dnduser
sudo usermod -aG docker dnduser

# Configure firewall
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp
sudo ufw enable

# Disable root login
sudo nano /etc/ssh/sshd_config
# Set: PermitRootLogin no
sudo systemctl restart ssh
```

### Application Security
- Use strong passwords in `.env.production`
- Enable Cloudflare security features
- Regular backups to cloud storage
- Monitor logs for suspicious activity

## 🔄 **Mobile Workflow Benefits**

### ✅ **Advantages:**
- **Location Independent:** Works from anywhere with internet
- **No Router Setup:** No need to configure routers at each location
- **Professional Setup:** Static IP, proper domain, SSL certificates
- **Always Available:** 24/7 uptime for your players
- **Backup Included:** Cloud providers offer backup services
- **Scalable:** Easy to upgrade if you need more resources

### ✅ **Perfect for Your Use Case:**
- Moving between locations frequently
- Don't want to depend on local network configuration
- Need reliable access for D&D sessions
- Want professional appearance for players

## 📱 **Alternative: Mobile Hotspot Setup**

If you prefer running locally but want mobility:

### Mobile Hotspot + VPN Solution
1. **Use mobile hotspot** for internet
2. **Set up VPN server** on cloud (WireGuard/OpenVPN)
3. **Tunnel traffic** through VPN to get static IP
4. **Point domain** to VPN server IP

This is more complex but keeps your laptop as the server.

## 🎯 **Recommended Approach**

For your mobile lifestyle, I recommend:

1. **DigitalOcean Droplet** ($6/month)
2. **Cloudflare domain** (karsusinitiative.com)
3. **Git-based deployment** workflow
4. **Local development** on laptop
5. **Cloud production** hosting

This gives you:
- ✅ Complete location independence
- ✅ Professional setup
- ✅ Easy development workflow
- ✅ Reliable uptime for players
- ✅ No router configuration needed

## 🚀 **Ready to Deploy to Cloud?**

Would you like me to:
1. Create cloud deployment scripts
2. Set up automated deployment workflow
3. Configure cloud-specific security
4. Create management scripts for cloud server

Your D&D sessions will be accessible from anywhere! 🎲
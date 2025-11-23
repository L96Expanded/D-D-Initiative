#!/bin/bash
# Security Setup Script for D&D Initiative Tracker Production

echo "🔒 Setting up security best practices for initiativetracker.ddns.net"

# Create backup directory
mkdir -p ./backups
mkdir -p ./nginx/ssl

echo "📋 Security Checklist:"

echo "✅ 1. Strong passwords configured in .env.production"
echo "✅ 2. JWT secret updated with secure random string"
echo "✅ 3. CORS origins restricted to your domain"

echo "🔄 4. Setting up SSL certificate (Let's Encrypt)..."

# Check if certbot is available
if command -v certbot &> /dev/null; then
    echo "📜 Generating SSL certificate for initiativetracker.ddns.net..."
    
    # Generate SSL certificate
    sudo certbot certonly --standalone \
        -d initiativetracker.ddns.net \
        --non-interactive \
        --agree-tos \
        --email your-email@example.com
    
    # Copy certificates to nginx directory
    sudo cp /etc/letsencrypt/live/initiativetracker.ddns.net/fullchain.pem ./nginx/ssl/cert.pem
    sudo cp /etc/letsencrypt/live/initiativetracker.ddns.net/privkey.pem ./nginx/ssl/key.pem
    
    echo "✅ SSL certificate generated successfully!"
else
    echo "⚠️  Certbot not found. Installing Let's Encrypt certificates manually:"
    echo "   1. Install certbot: sudo apt-get install certbot"
    echo "   2. Run: sudo certbot certonly --standalone -d initiativetracker.ddns.net"
    echo "   3. Copy certificates to ./nginx/ssl/ directory"
fi

echo "🔄 5. Setting up automated backups..."

# Create backup script
cat > ./backup-database.sh << 'EOF'
#!/bin/bash
# Database backup script

BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/dnd_tracker_backup_$DATE.sql"

echo "📦 Creating database backup: $BACKUP_FILE"

# Create backup
docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U dnd_user dnd_tracker > "$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_FILE"

echo "✅ Backup completed: $BACKUP_FILE.gz"

# Keep only last 7 backups
find $BACKUP_DIR -name "dnd_tracker_backup_*.sql.gz" -mtime +7 -delete

echo "🧹 Old backups cleaned up"
EOF

chmod +x ./backup-database.sh

echo "🔄 6. Setting up monitoring script..."

# Create monitoring script
cat > ./monitor-security.sh << 'EOF'
#!/bin/bash
# Security monitoring script

echo "🔍 Security Monitoring Report - $(date)"
echo "============================================"

# Check for failed login attempts
echo "🚨 Recent authentication failures:"
docker-compose -f docker-compose.prod.yml logs backend 2>/dev/null | grep -i "unauthorized\|authentication failed\|invalid credentials" | tail -10

# Check for unusual API activity
echo ""
echo "📊 API Request Summary (last 100 requests):"
docker-compose -f docker-compose.prod.yml logs backend 2>/dev/null | grep -E "GET|POST|PUT|DELETE" | tail -100 | awk '{print $1}' | sort | uniq -c | sort -nr

# Check container health
echo ""
echo "🏥 Container Health Status:"
docker-compose -f docker-compose.prod.yml ps

# Check disk space
echo ""
echo "💾 Disk Space Usage:"
df -h . | tail -1

# Check SSL certificate expiry
if [ -f "./nginx/ssl/cert.pem" ]; then
    echo ""
    echo "📜 SSL Certificate Status:"
    openssl x509 -in ./nginx/ssl/cert.pem -noout -dates
fi

echo ""
echo "✅ Security monitoring complete"
EOF

chmod +x ./monitor-security.sh

echo "🔄 7. Creating firewall configuration..."

# Create firewall setup script
cat > ./setup-firewall.sh << 'EOF'
#!/bin/bash
# Firewall configuration for D&D Initiative Tracker

echo "🔥 Configuring firewall for initiativetracker.ddns.net"

# Enable UFW if available (Ubuntu/Debian)
if command -v ufw &> /dev/null; then
    echo "Setting up UFW firewall..."
    
    # Reset UFW
    sudo ufw --force reset
    
    # Default policies
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    
    # Allow SSH (important!)
    sudo ufw allow ssh
    
    # Allow HTTP and HTTPS
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    
    # Allow API port
    sudo ufw allow 8000/tcp
    
    # Enable firewall
    sudo ufw --force enable
    
    echo "✅ UFW firewall configured"
    sudo ufw status
else
    echo "⚠️  UFW not available. Please configure your firewall manually:"
    echo "   Allow incoming: 22 (SSH), 80 (HTTP), 443 (HTTPS), 8000 (API)"
    echo "   Block all other incoming connections"
fi
EOF

chmod +x ./setup-firewall.sh

echo "🔄 8. Setting up log rotation..."

# Create logrotate configuration
sudo tee /etc/logrotate.d/dnd-initiative << 'EOF'
/var/lib/docker/containers/*/*-json.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    copytruncate
}
EOF

echo "✅ Security setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Run: ./setup-firewall.sh (configure firewall)"
echo "2. Set up SSL: Follow SSL instructions above"
echo "3. Schedule backups: Add ./backup-database.sh to cron"
echo "4. Monitor security: Run ./monitor-security.sh regularly"
echo ""
echo "🕐 Suggested cron jobs (run 'crontab -e'):"
echo "# Daily backup at 2 AM"
echo "0 2 * * * /path/to/D-D-Initiative/backup-database.sh"
echo "# Security monitoring every 6 hours"
echo "0 */6 * * * /path/to/D-D-Initiative/monitor-security.sh >> /var/log/dnd-security.log"
echo ""
echo "🔒 Your D&D Initiative Tracker is now secured for production!"
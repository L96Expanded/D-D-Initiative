# Router Configuration Guide for initiativetracker.ddns.net

## Step 1: Find Your Computer's Local IP Address

1. **Open Command Prompt** and run:
   ```cmd
   ipconfig
   ```
2. **Look for** "IPv4 Address" under your active network adapter
3. **Note down** your local IP (e.g., 192.168.1.100)

## Step 2: Access Your Router's Admin Panel

1. **Open a web browser** and go to one of these common router addresses:
   - http://192.168.1.1
   - http://192.168.0.1
   - http://10.0.0.1
   - http://192.168.1.254

2. **Login** with your router credentials (often on a sticker on the router)

## Step 3: Configure Port Forwarding

### Required Port Forwarding Rules:

| Service | External Port | Internal Port | Internal IP | Protocol |
|---------|---------------|---------------|-------------|----------|
| HTTP Web | 80 | 80 | YOUR_LOCAL_IP | TCP |
| API | 8000 | 8000 | YOUR_LOCAL_IP | TCP |
| HTTPS (future) | 443 | 443 | YOUR_LOCAL_IP | TCP |

### Router-Specific Instructions:

**For most routers:**
1. Find **"Port Forwarding"**, **"Virtual Server"**, or **"NAT"** section
2. Click **"Add New Rule"** or **"+"**
3. **Configure each rule**:

**Rule 1 - Web Frontend:**
- Name: D&D Initiative Web
- External Port: 80
- Internal Port: 80
- Internal IP: [YOUR_LOCAL_IP]
- Protocol: TCP
- Enabled: Yes

**Rule 2 - API Backend:**
- Name: D&D Initiative API
- External Port: 8000
- Internal Port: 8000
- Internal IP: [YOUR_LOCAL_IP]
- Protocol: TCP
- Enabled: Yes

**Rule 3 - HTTPS (Optional):**
- Name: D&D Initiative HTTPS
- External Port: 443
- Internal Port: 443
- Internal IP: [YOUR_LOCAL_IP]
- Protocol: TCP
- Enabled: Yes

4. **Save/Apply** changes
5. **Reboot router** if required

## Step 4: Test Port Forwarding

1. **From your phone** (using mobile data, not WiFi):
   - Visit: http://initiativetracker.ddns.net
   - API Test: http://initiativetracker.ddns.net:8000/docs

2. **Or use online tools**:
   - https://www.yougetsignal.com/tools/open-ports/
   - Test ports 80 and 8000 with your external IP

## Step 5: Update Dynamic DNS

1. **Login to your DDNS provider** (where you registered initiativetracker.ddns.net)
2. **Update the A record** to point to your current external IP
3. **Set up automatic updates** if available

## Troubleshooting

**Ports don't show as open:**
- Double-check your local IP address hasn't changed
- Verify router settings were saved correctly
- Try rebooting the router
- Check if your ISP blocks these ports

**Can't access router admin:**
- Try different IP addresses listed above
- Check router documentation
- Reset router to factory defaults (last resort)

**Connection works locally but not externally:**
- Verify your external IP hasn't changed
- Check DDNS is pointing to correct IP
- Test with mobile data instead of WiFi
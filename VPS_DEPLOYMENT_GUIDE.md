# VPS Deployment Guide - King's Choice Management App

## 🚀 Quick Start

### For Linux VPS (Ubuntu/Debian/CentOS):

1. **Upload files to your VPS**:
   ```bash
   scp -r . user@your-vps-ip:/home/user/kings-choice/
   ```

2. **Connect to your VPS**:
   ```bash
   ssh user@your-vps-ip
   cd /home/user/kings-choice/
   ```

3. **Run the installation script**:
   ```bash
   chmod +x install_and_start.sh
   ./install_and_start.sh
   ```

4. **Access your application**:
   - Open browser to `http://your-vps-ip:5000`

### For Windows VPS:

1. **Upload files to your VPS**
2. **Open Command Prompt as Administrator**
3. **Navigate to the app directory**
4. **Run the installation script**:
   ```cmd
   install_and_start.bat
   ```

## 📋 What the Script Does

### Automatic Setup:
- ✅ Installs Python 3 (if not present)
- ✅ Creates virtual environment
- ✅ Installs all dependencies
- ✅ Sets up environment variables
- ✅ Creates necessary directories
- ✅ Migrates database (adds SubUser table)
- ✅ Creates systemd service (Linux)
- ✅ Starts application in background
- ✅ Sets up management scripts

### Created Files:
- `start_app.sh` / `start_app.bat` - Start the application
- `stop_app.sh` / `stop_app.bat` - Stop the application
- `status_app.sh` / `status_app.bat` - Check application status
- `.env` - Environment configuration
- `venv/` - Python virtual environment

## 🔧 Manual Commands

### Linux Service Management:
```bash
# Start application
sudo systemctl start kings-choice.service

# Stop application
sudo systemctl stop kings-choice.service

# Restart application
sudo systemctl restart kings-choice.service

# Check status
sudo systemctl status kings-choice.service

# View logs
sudo journalctl -u kings-choice.service -f
```

### Windows Service Management:
```cmd
# Start application
start_app.bat

# Stop application
stop_app.bat

# Check status
status_app.bat
```

## 🌐 Access Your Application

### Local Access:
- `http://localhost:5000`

### Network Access:
- `http://your-vps-ip:5000`

### Default Users:
- **Admin**: knotico (if created)
- **Regular User**: Julija (if created)
- **Sub-User**: julija_helper (if created)

## 🔒 Security Considerations

### Firewall Setup (Linux):
```bash
# Allow port 5000
sudo ufw allow 5000

# Or for specific IP only
sudo ufw allow from YOUR_IP to any port 5000
```

### Firewall Setup (Windows):
```cmd
# Allow port 5000 through Windows Firewall
netsh advfirewall firewall add rule name="Kings Choice App" dir=in action=allow protocol=TCP localport=5000
```

## 📊 Monitoring

### Check Application Status:
```bash
# Linux
./status_app.sh

# Windows
status_app.bat
```

### View Logs:
```bash
# Linux
sudo journalctl -u kings-choice.service -f

# Windows
# Check the application window or logs folder
```

## 🔄 Updates

### Update Application:
```bash
# Pull latest changes
git pull origin main

# Restart application
sudo systemctl restart kings-choice.service
```

## 🆘 Troubleshooting

### Application Won't Start:
1. Check if port 5000 is in use:
   ```bash
   netstat -tulpn | grep :5000
   ```

2. Check logs:
   ```bash
   sudo journalctl -u kings-choice.service -f
   ```

3. Check database:
   ```bash
   sqlite3 kings_choice.db ".tables"
   ```

### Permission Issues:
```bash
# Fix file permissions
chmod +x *.sh
chown -R $USER:$USER .
```

### Database Issues:
```bash
# Recreate database
rm kings_choice.db
python3 -c "from app import app; from database import create_all_tables; create_all_tables(app)"
```

## 📁 File Structure

```
kings-choice/
├── app.py                    # Main application
├── models.py                 # Database models
├── auth.py                   # Authentication
├── database.py               # Database configuration
├── config.py                 # App configuration
├── requirements.txt          # Python dependencies
├── install_and_start.sh      # Linux installation script
├── install_and_start.bat     # Windows installation script
├── start_app.sh              # Start script (Linux)
├── start_app.bat             # Start script (Windows)
├── stop_app.sh               # Stop script (Linux)
├── stop_app.bat              # Stop script (Windows)
├── status_app.sh             # Status script (Linux)
├── status_app.bat            # Status script (Windows)
├── .env                      # Environment variables
├── venv/                     # Python virtual environment
├── kings_choice.db           # SQLite database
├── templates/                # HTML templates
├── static/                   # Static files
├── routes/                   # Route handlers
└── logs/                     # Application logs
```

## 🎯 Next Steps

1. **Create Admin User** (if not exists):
   ```bash
   python3 create_admin.py
   ```

2. **Create Sub-Users** (optional):
   ```bash
   python3 create_subuser.py Julija julija_helper julija.helper@example.com helper123
   ```

3. **Configure Domain** (optional):
   - Set up reverse proxy with Nginx
   - Configure SSL certificate
   - Set up custom domain

4. **Backup Setup**:
   ```bash
   # Create backup script
   echo "cp kings_choice.db backup_$(date +%Y%m%d_%H%M%S).db" > backup.sh
   chmod +x backup.sh
   ```

Your King's Choice Management App is now ready for production use! 🎉

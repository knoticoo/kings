# Multi-User King's Choice Management - Usage Guide

## 🚀 Quick Start

### Simple Way (Recommended)
```bash
python start_multi_user.py start
```

### Manual Way
```bash
python setup_multi_user.py  # One-time setup
python app.py               # Start in foreground
```

## 📋 Available Commands

### Application Management
```bash
python start_multi_user.py start      # Start in background
python start_multi_user.py start-fg   # Start in foreground
python start_multi_user.py stop       # Stop application
python start_multi_user.py restart    # Restart application
python start_multi_user.py status     # Show status
```

### Monitoring & Logs
```bash
python start_multi_user.py logs 100   # Show last 100 log lines
python start_multi_user.py monitor    # Auto-restart on crash
python start_multi_user.py cleanup    # Clean old files
```

### Setup & Maintenance
```bash
python start_multi_user.py install    # Install dependencies only
python start_multi_user.py setup      # Setup database only
```

## ✅ Your Questions Answered

### 1. **Will it run in background?** ✅ YES
```bash
python start_multi_user.py start
```
- Runs in background automatically
- Saves PID to `app.pid`
- Logs to `logs/app.log` and `logs/error.log`
- Access at `http://localhost:5000`

### 2. **Will it kill process when restart?** ✅ YES
```bash
python start_multi_user.py restart
```
- Gracefully stops the current process
- Waits for clean shutdown (10 seconds)
- Force kills if needed
- Starts fresh process
- Cleans up PID file

### 3. **Will it install all dependencies?** ✅ YES
```bash
python start_multi_user.py start
```
- Automatically installs from `requirements.txt`
- Sets up database if needed
- Handles all dependencies including new ones (psutil)

## 🔧 Process Management Features

### Background Running
- **PID Management**: Saves process ID to `app.pid`
- **Log Files**: Separate logs for output and errors
- **Process Detection**: Checks if app is actually running
- **Clean Shutdown**: Graceful termination with fallback

### Auto-Restart
```bash
python start_multi_user.py monitor
```
- Monitors application every 5 seconds
- Auto-restarts if it crashes
- Configurable max restart attempts
- Stops monitoring on Ctrl+C

### Status Monitoring
```bash
python start_multi_user.py status
```
Shows:
- ✅ Running status
- 📊 Memory usage
- 💻 CPU usage
- ⏱️ Uptime
- 🌐 URL access
- ❤️ Health check

## 📁 File Structure

```
/workspace/
├── start_multi_user.py          # New production script
├── app.pid                      # Process ID file
├── app_config.json              # Configuration file
├── logs/
│   ├── app.log                  # Application logs
│   └── error.log                # Error logs
└── user_databases/              # User databases
    ├── admin_admin.db
    └── user_1_username.db
```

## 🎯 Production Usage

### Start Application
```bash
python start_multi_user.py start
```

### Check Status
```bash
python start_multi_user.py status
```

### View Logs
```bash
python start_multi_user.py logs
```

### Stop Application
```bash
python start_multi_user.py stop
```

### Restart Application
```bash
python start_multi_user.py restart
```

## 🔄 Migration from Old System

### Old System (Obsolete)
```bash
./start.sh install    # Complex setup
./start.sh start      # Start application
./start.sh status     # Check status
./start.sh logs       # View logs
./start.sh stop       # Stop application
```

### New System (Current)
```bash
python start_multi_user.py start      # Simple start
python start_multi_user.py status     # Check status
python start_multi_user.py logs       # View logs
python start_multi_user.py stop       # Stop application
```

## ⚙️ Configuration

The script creates `app_config.json` with these settings:
```json
{
  "port": 5000,
  "host": "0.0.0.0",
  "workers": 1,
  "auto_restart": true,
  "max_restarts": 5,
  "restart_delay": 5
}
```

## 🚨 Troubleshooting

### Application Won't Start
1. Check dependencies: `python start_multi_user.py install`
2. Check database: `python start_multi_user.py setup`
3. Check logs: `python start_multi_user.py logs`

### Application Keeps Crashing
1. Check error logs: `cat logs/error.log`
2. Run in foreground: `python start_multi_user.py start-fg`
3. Check system resources: `python start_multi_user.py status`

### Port Already in Use
1. Stop other applications using port 5000
2. Or change port in `app_config.json`

## 🎉 Benefits

### ✅ **Background Running**
- Runs in background automatically
- No need to keep terminal open
- Proper process management

### ✅ **Process Management**
- Graceful shutdown
- Force kill if needed
- PID file management
- Process monitoring

### ✅ **Dependency Management**
- Auto-installs dependencies
- Handles all requirements
- Database setup included

### ✅ **Production Ready**
- Log management
- Error handling
- Auto-restart capability
- Status monitoring

---

**The new `start_multi_user.py` script replaces the old `start.sh` and provides all the functionality you need for production deployment!**
# VPS Application Startup Troubleshooting Guide

## 🚨 Issue: Application Failed to Start After SubUser Update

The application is failing to start on your VPS because the database doesn't have the new SubUser table that was added in the latest update.

## 🔧 Quick Fix

### Step 1: Upload Migration Script
Upload the `vps_subuser_migration.py` script to your VPS.

### Step 2: Run Migration
```bash
python3 vps_subuser_migration.py
```

### Step 3: Start Application
```bash
python3 app.py
```

## 🔍 Detailed Troubleshooting

### Check Current Status
```bash
# Check if Python processes are running
ps aux | grep python

# Check if port 5000 is in use
netstat -tulpn | grep :5000

# Check application logs
tail -f app.log
```

### Common Issues and Solutions

#### 1. Database Schema Error
**Error**: `no such table: sub_users`
**Solution**: Run the migration script
```bash
python3 vps_subuser_migration.py
```

#### 2. Import Error
**Error**: `ImportError: cannot import name 'SubUser'`
**Solution**: Make sure you have the latest code
```bash
git pull origin main
```

#### 3. Permission Error
**Error**: `Permission denied`
**Solution**: Check file permissions
```bash
chmod +x vps_subuser_migration.py
chmod 644 kings_choice.db
```

#### 4. Port Already in Use
**Error**: `Address already in use`
**Solution**: Kill existing processes
```bash
pkill -f python
# or
fuser -k 5000/tcp
```

## 🛠️ Manual Database Fix

If the migration script doesn't work, you can manually add the table:

```sql
-- Connect to your database
sqlite3 kings_choice.db

-- Add the SubUser table
CREATE TABLE sub_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    parent_user_id INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    permissions TEXT DEFAULT '{}',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    FOREIGN KEY (parent_user_id) REFERENCES users(id)
);

-- Exit SQLite
.quit
```

## 🔄 Complete VPS Update Process

### 1. Stop Application
```bash
pkill -f python
```

### 2. Backup Database
```bash
cp kings_choice.db kings_choice_backup_$(date +%Y%m%d_%H%M%S).db
```

### 3. Update Code
```bash
git pull origin main
```

### 4. Run Migration
```bash
python3 vps_subuser_migration.py
```

### 5. Start Application
```bash
python3 app.py
```

### 6. Check Status
```bash
curl http://localhost:5000
```

## 📋 Verification Steps

After running the migration, verify everything works:

1. **Check Database**:
   ```bash
   sqlite3 kings_choice.db ".tables"
   ```
   Should show `sub_users` table.

2. **Test Application**:
   ```bash
   curl -I http://localhost:5000
   ```
   Should return HTTP 200.

3. **Check Logs**:
   ```bash
   tail -f app.log
   ```
   Should show no errors.

## 🆘 Emergency Rollback

If something goes wrong, you can rollback:

```bash
# Stop application
pkill -f python

# Restore database backup
cp kings_choice_backup_*.db kings_choice.db

# Start with old code
git checkout HEAD~1
python3 app.py
```

## 📞 Support

If you're still having issues:

1. Check the application logs
2. Verify database file permissions
3. Ensure all dependencies are installed
4. Check Python version compatibility

The migration script should resolve the startup issue by adding the missing SubUser table to your VPS database.

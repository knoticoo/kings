# Migration Guide: From Single-User to Multi-User System

## 🚨 Important Changes

### Start Script is Now Obsolete

The original `start.sh` script is **no longer needed** for the multi-user system. The new setup is much simpler and more reliable.

## Migration Steps

### 1. Backup Your Current System
```bash
# Backup your current database
cp kings_choice.db kings_choice_backup.db

# Backup any custom configurations
cp -r static/uploads static/uploads_backup 2>/dev/null || true
```

### 2. Install New Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Multi-User Setup
```bash
python setup_multi_user.py
```

### 4. Start the New System
```bash
python app.py
```

## What Changed

### Old System (Single-User)
```bash
# Complex setup with virtual environment
./start.sh install
./start.sh start
./start.sh status
./start.sh logs
./start.sh stop
```

### New System (Multi-User)
```bash
# Simple setup
python setup_multi_user.py  # One-time setup
python app.py               # Start application
```

## Benefits of New System

### ✅ Simplified Deployment
- **No Virtual Environment**: Works with system Python
- **No Complex Scripts**: Direct Python execution
- **Faster Setup**: Reduced complexity
- **More Reliable**: Fewer moving parts

### ✅ Multi-User Features
- **User Authentication**: Login/logout system
- **Data Isolation**: Each user has separate database
- **Individual Notifications**: Each user gets their own Telegram/Discord
- **Admin Panel**: Manage all users from one interface

### ✅ Better Security
- **Password Hashing**: Secure password storage
- **Session Management**: Proper user sessions
- **Data Privacy**: Complete user data isolation
- **Access Control**: Users can only access their own data

## File Changes

### New Files Added
```
auth.py                          # Authentication system
database_manager.py              # User database management
user_notifications.py           # Individual notifications
setup_multi_user.py             # Simple setup script
test_multi_user.py              # System testing
templates/auth/                  # Authentication templates
```

### Files No Longer Needed
```
start.sh                        # Obsolete - use python app.py instead
```

### Modified Files
```
app.py                          # Added authentication
models.py                       # Added User model
requirements.txt                # Added auth dependencies
templates/base.html             # Added user menu
```

## Data Migration

### If You Have Existing Data
1. **Run Setup**: `python setup_multi_user.py`
2. **Create User**: Create a user account for your existing data
3. **Manual Migration**: Copy data from old database to new user database
4. **Configure Notifications**: Set up Telegram/Discord for the user

### Database Structure
- **Old**: Single `kings_choice.db` with all data
- **New**: Main `kings_choice.db` for users + individual user databases

## Troubleshooting

### Common Issues
1. **Import Errors**: Make sure all dependencies are installed
2. **Database Errors**: Run the setup script to initialize databases
3. **Permission Errors**: Check file permissions for database files
4. **Port Conflicts**: Make sure port 5000 is available

### Getting Help
1. Check the logs for error messages
2. Run the test script: `python test_multi_user.py`
3. Verify all files are in place
4. Check Python version (3.8+ required)

## Rollback Plan

If you need to go back to the single-user system:
1. **Restore Backup**: `cp kings_choice_backup.db kings_choice.db`
2. **Remove New Files**: Delete auth.py, database_manager.py, etc.
3. **Restore Original**: Use git to restore original files
4. **Use Old Script**: `./start.sh start`

## Summary

The new multi-user system is:
- **Simpler to deploy** (no complex scripts)
- **More secure** (user authentication)
- **More scalable** (multiple users)
- **More flexible** (individual notifications)
- **Easier to maintain** (cleaner code)

The old `start.sh` script is completely obsolete and should not be used with the new system.
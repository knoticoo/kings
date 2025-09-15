# King's Choice Management - Multi-User System

## 🚀 Quick Start

### 1. Setup (One-time)
```bash
python setup_multi_user.py
```

### 2. Start Application
```bash
python app.py
```

### 3. Access System
- Go to `http://localhost:5000`
- Login with admin credentials
- Create users via admin panel

## ⚠️ Important: Start Script is Obsolete

The original `start.sh` script is **no longer needed**. The new multi-user system uses a much simpler approach:

### Old Way (Single-User):
```bash
./start.sh install  # Complex setup
./start.sh start    # Start application
```

### New Way (Multi-User):
```bash
python setup_multi_user.py  # Simple setup
python app.py               # Start application
```

## 🎯 Key Features

- **Multi-User Support**: Each user has their own isolated database
- **Individual Notifications**: Each user gets their own Telegram/Discord channels
- **Admin Panel**: Create and manage users
- **Data Isolation**: Users cannot see each other's data
- **User Settings**: Each user can configure their own notifications

## 📁 New Files

- `auth.py` - Authentication system
- `database_manager.py` - User database management
- `user_notifications.py` - Individual notification service
- `setup_multi_user.py` - Setup script
- `test_multi_user.py` - Test script
- `templates/auth/` - Authentication templates

## 📚 Documentation

- `MULTI_USER_SETUP.md` - Complete setup guide
- `MIGRATION_GUIDE.md` - Migration from single-user
- `MULTI_USER_PR.md` - Pull request details

## 🔧 Requirements

- Python 3.8+
- Dependencies in `requirements.txt`
- No virtual environment needed
- No complex shell scripts

## 🎉 Benefits

- **Simpler**: No complex setup scripts
- **Faster**: Direct Python execution
- **More Secure**: User authentication and data isolation
- **Scalable**: Easy to add more users
- **Flexible**: Individual notification channels

---

**The old `start.sh` script is completely obsolete and should not be used with the new multi-user system.**
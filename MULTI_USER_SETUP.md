# Multi-User King's Choice Management System

This document explains how to set up and use the multi-user version of the King's Choice Management application.

## Features

### 🔐 User Authentication
- **Login/Logout System**: Secure authentication using Flask-Login
- **Admin Panel**: Create and manage users (admin only)
- **User Settings**: Each user can configure their own Telegram/Discord settings

### 🗄️ Data Isolation
- **Separate Databases**: Each user has their own isolated database file
- **User-Specific Data**: Players, alliances, events, and guides are completely separate
- **No Cross-User Access**: Users cannot see or access other users' data

### 📱 Multi-Platform Notifications
- **Individual Telegram Bots**: Each user can configure their own Telegram bot
- **Individual Discord Bots**: Each user can configure their own Discord bot
- **Independent Notifications**: MVP and winner announcements go to user-specific channels

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Setup Script
```bash
python setup_multi_user.py
```

This will:
- Initialize the main database
- Create the first admin user
- Set up the user database structure
- Allow you to configure Telegram/Discord for the admin user

### 3. Start the Application
```bash
python app.py
```

### 4. Access the System
- Open your browser to `http://localhost:5000`
- Login with your admin credentials
- Access the admin panel at `/admin/users` to create additional users

## ⚠️ Important: Start Script No Longer Needed

The original `start.sh` script is **obsolete** for the multi-user system. The new setup process is much simpler:

### Old Way (Single-User):
```bash
./start.sh install  # Complex setup with virtual environment
./start.sh start    # Start application
```

### New Way (Multi-User):
```bash
python setup_multi_user.py  # Simple setup
python app.py               # Start application
```

The multi-user system handles everything automatically and doesn't require the complex shell script setup. The new approach is:
- **Simpler**: No virtual environment management needed
- **Faster**: Direct Python execution
- **Cleaner**: No complex shell script dependencies
- **More Reliable**: Fewer moving parts

## User Management

### Admin Functions
- **Create Users**: Add new users with their own databases
- **Configure Notifications**: Set up Telegram and Discord for each user
- **User Status**: Activate/deactivate user accounts
- **Delete Users**: Remove users and their data (admin cannot delete themselves)

### User Functions
- **Personal Settings**: Configure own Telegram/Discord settings
- **Isolated Data**: Manage their own players, alliances, events, and guides
- **Independent Notifications**: Receive notifications only for their own data

## Database Structure

### Main Database (`kings_choice.db`)
- **Users table**: Stores user accounts and configuration
- **Authentication**: Login credentials and permissions

### User Databases (`user_databases/user_X_username.db`)
Each user has their own database containing:
- **Players**: Game players (isolated per user)
- **Alliances**: Player groups (isolated per user)
- **Events**: Game events (isolated per user)
- **MVP Assignments**: MVP tracking (isolated per user)
- **Winner Assignments**: Winner tracking (isolated per user)
- **Guides**: Guide articles (isolated per user)
- **Blacklist**: Blacklisted players/alliances (isolated per user)

## Notification Configuration

### Telegram Setup
1. Create a bot with @BotFather on Telegram
2. Get the bot token
3. Add the bot to your channel/group
4. Get the chat ID (use @userinfobot)
5. Configure in user settings

### Discord Setup
1. Create a bot in Discord Developer Portal
2. Get the bot token
3. Add the bot to your server with appropriate permissions
4. Get the channel ID (right-click channel → Copy ID)
5. Configure in user settings

## Security Features

- **Password Hashing**: All passwords are securely hashed using Werkzeug
- **Session Management**: Secure session handling with Flask-Login
- **Data Isolation**: Complete separation of user data
- **Admin Protection**: Admins cannot delete their own accounts
- **Input Validation**: All user inputs are validated and sanitized

## File Structure

```
/workspace/
├── app.py                          # Main Flask application
├── auth.py                         # Authentication module
├── database.py                     # Database initialization
├── database_manager.py             # User database management
├── models.py                       # Database models
├── user_notifications.py           # Notification service
├── setup_multi_user.py             # Setup script
├── create_admin.py                 # Admin creation script
├── user_databases/                 # User-specific databases
│   ├── admin_admin.db
│   ├── user_1_username.db
│   └── ...
├── templates/
│   ├── auth/                       # Authentication templates
│   │   ├── login.html
│   │   ├── admin_users.html
│   │   ├── create_user.html
│   │   └── user_settings.html
│   └── ...
└── routes/                         # Application routes
    ├── main_routes.py
    ├── player_routes.py
    └── ...
```

## Usage Examples

### Creating a New User (Admin)
1. Login as admin
2. Go to User Management
3. Click "Create User"
4. Fill in user details
5. Configure Telegram/Discord (optional)
6. Save user

### Configuring Notifications (User)
1. Login to your account
2. Click on your username → Settings
3. Enter Telegram bot token and chat ID
4. Enter Discord bot token and channel ID
5. Enable desired notification types
6. Save settings

### Managing Game Data (User)
1. Login to your account
2. Use the dashboard to manage players, alliances, events
3. All data is automatically isolated to your account
4. Notifications will be sent to your configured channels

## Troubleshooting

### Common Issues
1. **Database not found**: Run the setup script again
2. **Login issues**: Check username/password, ensure user is active
3. **Notification failures**: Verify bot tokens and channel IDs
4. **Permission errors**: Ensure you have admin privileges for user management

### Support
- Check the application logs for detailed error messages
- Verify all configuration settings are correct
- Ensure all required dependencies are installed

## Migration from Single-User

If you have an existing single-user installation:
1. Backup your current database
2. Run the setup script
3. Create a user account for your existing data
4. Manually migrate data if needed (this is not automated)

## Security Recommendations

1. **Change Default Secret Key**: Update `SECRET_KEY` in app.py
2. **Use HTTPS**: Deploy with SSL certificates
3. **Regular Backups**: Backup both main and user databases
4. **Monitor Access**: Keep track of user activity
5. **Strong Passwords**: Enforce strong password policies
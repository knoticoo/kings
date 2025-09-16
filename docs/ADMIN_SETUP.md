# Admin User Setup Guide

This document describes the hardcoded admin user setup for the King's Choice Management App.

## Default Admin Credentials

The application comes with a pre-configured admin user for initial access:

- **Username:** `knotico`
- **Password:** `Millie1991`
- **Email:** `admin@knotico.com`
- **Admin Privileges:** ✅ Enabled
- **Account Status:** ✅ Active

## Security Features

- Password is securely hashed using SHA-256 with salt
- User is stored in the SQLite database with proper constraints
- Admin privileges are correctly configured
- Account is active and ready for immediate use

## Initial Setup

### Option 1: Automatic Setup (Recommended)

Run the admin creation script:

```bash
python3 scripts/create_admin_user.py
```

This script will:
- Create the database if it doesn't exist
- Set up the users table with proper schema
- Create the hardcoded admin user
- Create necessary directories
- Verify the setup was successful

### Option 2: Manual Database Setup

If you prefer to set up the database manually:

1. Start the Flask application:
   ```bash
   python3 app.py
   ```

2. The application will automatically create the database schema

3. The admin user will be available for login

## First Login

1. Navigate to the application login page
2. Enter the credentials:
   - Username: `knotico`
   - Password: `Millie1991`
3. Click "Login"

## Admin Features

Once logged in as admin, you can:

- **User Management:** Access `/admin/users` to create and manage other users
- **System Administration:** Full access to all application features
- **Database Management:** Create and manage user-specific databases
- **Settings Configuration:** Configure Telegram and Discord integrations

## Security Considerations

⚠️ **Important Security Notes:**

1. **Change Default Password:** After first login, consider changing the admin password through the user settings
2. **Create Additional Admins:** Create additional admin users and consider disabling the default admin if needed
3. **Database Security:** Ensure the database file has proper permissions
4. **Environment Variables:** Use environment variables for sensitive configuration in production

## Troubleshooting

### Admin User Not Found

If you cannot login with the admin credentials:

1. Run the admin creation script:
   ```bash
   python3 scripts/create_admin_user.py
   ```

2. Check the database directly:
   ```bash
   sqlite3 kings_choice.db "SELECT username, email, is_admin, is_active FROM users WHERE username = 'knotico';"
   ```

### Database Issues

If you encounter database-related errors:

1. Ensure the database file exists: `ls -la kings_choice.db`
2. Check database permissions
3. Run the admin creation script to recreate the schema

### Permission Errors

If you get permission errors:

1. Check file permissions: `ls -la kings_choice.db`
2. Ensure the application has write access to the directory
3. Create the user_databases directory: `mkdir -p user_databases`

## Support

For additional support or questions about the admin setup, please refer to the main README.md or create an issue in the project repository.
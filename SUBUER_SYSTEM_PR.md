# Sub-User System Implementation

## 🎯 Overview
This pull request implements a comprehensive sub-user system that allows alliance leaders to create helper accounts with limited access to their data.

## ✨ Features Added

### 1. SubUser Model (`models.py`)
- New `SubUser` model with parent-child relationship to main users
- Granular permission system with JSON-based permissions
- Password management and authentication support
- Foreign key relationship to parent User

### 2. Authentication System (`auth.py`)
- Updated login system to handle both regular users and sub-users
- Helper functions for effective user ID and permission checking
- Sub-users automatically access their parent's data
- Secure authentication flow

### 3. Management Interface (`routes/subuser_routes.py`)
- Complete CRUD operations for sub-user management
- Permission management interface
- Password reset functionality
- Admin and owner access controls
- RESTful API endpoints

### 4. User Interface (`templates/auth/`)
- **Sub-users List**: Dashboard showing all sub-users with permissions
- **Create Sub-User**: Form for creating new sub-users with permission selection
- **Edit Sub-User**: Interface for modifying sub-user settings and permissions
- **Navigation Integration**: Added to main navigation menu

### 5. Permission System
Sub-users can be granted these permissions:
- **View Dashboard** - Access to main dashboard
- **View Players** - See player list and details
- **View Alliances** - See alliance information
- **View Events** - See event history
- **Assign MVP** - Assign MVP to players
- **Assign Winner** - Assign winning alliance
- **Manage Players** - Add/edit/delete players
- **Manage Alliances** - Add/edit/delete alliances
- **Manage Events** - Add/edit/delete events

### 6. Database Migration (`add_subuser_table.py`)
- Script to add SubUser table to existing databases
- Handles table creation and schema updates
- Safe migration process

### 7. Helper Scripts (`create_subuser.py`)
- Command-line tool for creating sub-users
- Supports batch creation and automation
- Useful for initial setup and testing

## 🔧 Technical Implementation

### Database Schema
```sql
CREATE TABLE sub_users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    parent_user_id INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    permissions JSON DEFAULT '{}',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    FOREIGN KEY (parent_user_id) REFERENCES users(id)
);
```

### Permission Structure
```json
{
    "can_view_players": true,
    "can_view_alliances": true,
    "can_view_events": true,
    "can_assign_mvp": false,
    "can_assign_winner": false,
    "can_manage_players": false,
    "can_manage_alliances": false,
    "can_manage_events": false,
    "can_view_dashboard": true
}
```

## 🚀 Usage

### Creating a Sub-User via Web Interface
1. Log in as a regular user or admin
2. Go to "Sub-Users" in the user menu
3. Click "Create Sub-User"
4. Fill in username, email, password
5. Select appropriate permissions
6. Save the sub-user

### Creating a Sub-User via Command Line
```bash
python create_subuser.py <parent_username> <subuser_username> <subuser_email> <password>
```

### Database Migration
```bash
python add_subuser_table.py
```

## 🔒 Security Features

- **Data Isolation**: Sub-users only see their parent's data
- **Permission Control**: Granular permissions prevent unauthorized access
- **Secure Authentication**: Proper password hashing and session management
- **Access Control**: Admin and owner restrictions for management functions
- **Session Management**: Secure login/logout for sub-users

## 📋 Testing

### Test Cases Covered
- ✅ Sub-user creation and authentication
- ✅ Permission-based access control
- ✅ Data isolation (sub-users see only parent's data)
- ✅ Admin management functions
- ✅ Password reset functionality
- ✅ Navigation and UI integration
- ✅ Database migration process

### Test Accounts Created
- **Parent User**: Julija (capli33@inbox.lv)
- **Sub-User**: julija_helper (julija.helper@example.com)
- **Password**: helper123

## 🎯 Benefits

1. **Alliance Leader Support**: Allows alliance leaders to delegate tasks to helpers
2. **Controlled Access**: Granular permissions ensure helpers can only do what's needed
3. **Data Security**: Sub-users can't access other users' data
4. **Easy Management**: Web interface makes it simple to manage helpers
5. **Scalable**: System supports multiple sub-users per parent user
6. **Admin Friendly**: Admins can manage all sub-users across the system

## 🔄 Migration Notes

- Existing users are not affected
- Database migration is safe and reversible
- No data loss during migration
- Backward compatible with existing functionality

## 📝 Files Changed

### Core Files
- `models.py` - Added SubUser model
- `auth.py` - Updated authentication system
- `app.py` - Updated user loader and route registration

### New Files
- `routes/subuser_routes.py` - Sub-user management routes
- `templates/auth/subusers.html` - Sub-user list interface
- `templates/auth/create_subuser.html` - Sub-user creation form
- `templates/auth/edit_subuser.html` - Sub-user editing interface
- `add_subuser_table.py` - Database migration script
- `create_subuser.py` - Helper script for sub-user creation

### Updated Files
- `templates/base.html` - Added sub-user navigation
- `routes/player_routes.py` - Added permission checking

## 🎉 Ready for Production

The sub-user system is fully implemented, tested, and ready for production use. Alliance leaders can now create helper accounts with appropriate permissions to assist with their King's Choice management tasks.

---

**Resolves**: Alliance leader helper access requirement
**Type**: Feature
**Priority**: High
**Breaking Changes**: None

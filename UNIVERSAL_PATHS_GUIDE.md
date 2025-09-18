# 🌍 Universal Path System for King's Choice Management App

## Overview

The King's Choice Management App now uses a **universal path system** that automatically adapts to different deployment environments without hardcoded paths. This makes the application portable and easy to deploy anywhere.

## 🎯 Key Features

- **Automatic Path Detection**: Detects the best data directory based on your environment
- **Environment Variable Override**: Easily customize paths via environment variables
- **Cross-Platform Compatible**: Works on VPS, containers, development environments
- **Migration Support**: Automatically migrates existing databases to new locations
- **XDG Standard Compliance**: Follows Linux filesystem standards when possible

## 📂 Path Resolution Priority

The system resolves database paths in this order:

1. **Explicit Environment Variables** (highest priority)
   - `KINGS_CHOICE_DATA_DIR` - Main data directory
   - `KINGS_CHOICE_MAIN_DB_PATH` - Main database file
   - `KINGS_CHOICE_USER_DB_DIR` - User databases directory

2. **XDG Data Directory** (Linux standard)
   - `$XDG_DATA_HOME/kings_choice`

3. **User Home Directory** (if not root)
   - `~/.local/share/kings_choice`

4. **Application Directory** (fallback)
   - `{app_directory}/data`

## 🚀 Quick Setup

### For VPS Deployment

1. **Copy your application to `/root/kings/`**
2. **Set your preferred data directory:**
   ```bash
   export KINGS_CHOICE_DATA_DIR=/root/kings_choice_data
   ```
3. **Run the setup script:**
   ```bash
   cd /root/kings
   python3 setup_universal_paths.py
   ```
4. **Start your application:**
   ```bash
   python3 app.py
   ```

### For Development

1. **Clone/copy the application anywhere**
2. **No environment variables needed** (uses automatic detection)
3. **Run the setup script:**
   ```bash
   python3 setup_universal_paths.py
   ```
4. **Start your application:**
   ```bash
   python3 app.py
   ```

## 🔧 Environment Configuration

Create a `.env` file in your application directory:

```bash
# Recommended: Set the main data directory
KINGS_CHOICE_DATA_DIR=/your/preferred/path

# Alternative: Set individual paths
# KINGS_CHOICE_MAIN_DB_PATH=/path/to/main/database.db
# KINGS_CHOICE_USER_DB_DIR=/path/to/user/databases

# Flask settings
SECRET_KEY=your-secret-key-here
```

## 📁 Directory Structure

The universal system creates this structure:

```
{DATA_DIRECTORY}/
├── kings_choice.db          # Main application database
└── user_databases/          # Individual user databases
    ├── user_1_admin.db
    ├── user_2_knotico.db
    └── user_3_julija.db
```

## 🔍 Deployment Examples

### VPS as Root
```bash
export KINGS_CHOICE_DATA_DIR=/root/kings_choice_data
```
**Result**: `/root/kings_choice_data/kings_choice.db`

### VPS as User
```bash
export KINGS_CHOICE_DATA_DIR=/home/username/kings_choice_data
```
**Result**: `/home/username/kings_choice_data/kings_choice.db`

### Docker Container
```bash
export KINGS_CHOICE_DATA_DIR=/app/data
```
**Result**: `/app/data/kings_choice.db`

### Development (No env vars)
**Result**: `~/.local/share/kings_choice/kings_choice.db`

## 🛠️ Migration from Old System

The setup script automatically:

1. **Detects existing databases** in common locations
2. **Migrates databases** to the new universal location
3. **Updates user database paths** in the main database
4. **Creates missing user databases**
5. **Generates environment configuration**

## 🔧 Troubleshooting

### Check Current Configuration
```bash
python3 -c "from config import Config; Config.print_config()"
```

### Verify Deployment Type
```bash
python3 -c "from config import Config; print(Config.detect_deployment_type())"
```

### Test Path Resolution
```bash
python3 -c "
from config import Config
print(f'Data dir: {Config.get_data_directory()}')
print(f'Main DB: {Config.get_main_database_path()}')
print(f'User DBs: {Config.get_user_database_directory()}')
"
```

## 📋 Benefits

- ✅ **No More Hardcoded Paths**: Works anywhere without code changes
- ✅ **Easy Deployment**: Set one environment variable and go
- ✅ **Automatic Migration**: Handles existing setups seamlessly  
- ✅ **Standard Compliance**: Follows Linux filesystem standards
- ✅ **Flexible Configuration**: Override any path as needed
- ✅ **Development Friendly**: Works out of the box for development

## 🔄 Upgrading Existing Installations

1. **Backup your current databases**
2. **Update your application files** (config.py, app.py, auth.py)
3. **Run the setup script**: `python3 setup_universal_paths.py`
4. **Review the generated .env file**
5. **Start your application normally**

The system will automatically detect and migrate your existing data!
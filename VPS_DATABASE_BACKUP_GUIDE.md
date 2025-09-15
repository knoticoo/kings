# VPS Database Backup & Restore Guide

This guide will help you backup your King's Choice database from your VPS before reinstalling, and restore it to your workspace.

## 🚀 Quick Start

### Step 1: Backup from VPS

1. **Upload the backup script to your VPS:**
   ```bash
   scp backup_vps.sh user@your-vps-ip:/home/user/
   scp backup_database.py user@your-vps-ip:/home/user/
   ```

2. **SSH into your VPS and update the database path:**
   ```bash
   ssh user@your-vps-ip
   nano backup_vps.sh
   # Update DB_PATH="/path/to/your/kings_choice.db" with your actual database path
   ```

3. **Run the backup script:**
   ```bash
   chmod +x backup_vps.sh
   ./backup_vps.sh
   ```

4. **Download the backup files:**
   ```bash
   # From your local machine
   scp user@your-vps-ip:/home/user/backups/kings_choice_backup_*.sql ./
   scp user@your-vps-ip:/home/user/backups/kings_choice_backup_*.db ./
   ```

### Step 2: Restore to Workspace

1. **Restore from SQL dump:**
   ```bash
   python3 backup_database.py restore kings_choice_backup_YYYYMMDD_HHMMSS.sql kings_choice.db
   ```

2. **Verify the restoration:**
   ```bash
   python3 backup_database.py verify kings_choice.db
   ```

## 📋 Detailed Instructions

### Method 1: Using the Backup Scripts (Recommended)

The provided scripts handle everything automatically:

- `backup_vps.sh` - Creates both SQL dump and binary backup on VPS
- `backup_database.py` - Python utility for backup/restore/verification

### Method 2: Manual SQLite Commands

If you prefer manual control:

**On VPS (backup):**
```bash
# Create SQL dump
sqlite3 kings_choice.db .dump > kings_choice_backup.sql

# Create binary backup
cp kings_choice.db kings_choice_backup.db

# Compress for easier transfer
tar -czf kings_choice_backup.tar.gz kings_choice_backup.*
```

**On Workspace (restore):**
```bash
# Extract if compressed
tar -xzf kings_choice_backup.tar.gz

# Restore from SQL dump
sqlite3 kings_choice.db < kings_choice_backup.sql

# Or restore from binary backup
cp kings_choice_backup.db kings_choice.db
```

### Method 3: Using Python Script Only

**On VPS:**
```bash
python3 backup_database.py backup /path/to/kings_choice.db
```

**On Workspace:**
```bash
python3 backup_database.py restore kings_choice_backup_YYYYMMDD_HHMMSS.sql kings_choice.db
```

## 🔍 Verification

After restoration, verify your database:

```bash
python3 backup_database.py verify kings_choice.db
```

This will show:
- All tables and their row counts
- Total number of records
- Database integrity status

## 🛠️ Troubleshooting

### Common Issues:

1. **"Database not found" error:**
   - Check the database path in `backup_vps.sh`
   - Ensure the database file exists and is readable

2. **Permission denied:**
   - Make sure the script is executable: `chmod +x backup_vps.sh`
   - Check file permissions on the database file

3. **SQLite not found:**
   - Install SQLite: `sudo apt-get install sqlite3` (Ubuntu/Debian)
   - Or use the Python script instead

4. **Restore fails:**
   - Check if the SQL dump file is complete
   - Verify the target database path is writable
   - Check for any error messages in the output

### File Locations:

- **VPS Backup Directory:** `./backups/` (relative to script location)
- **Workspace Database:** `./kings_choice.db`
- **Backup Files:** `kings_choice_backup_YYYYMMDD_HHMMSS.*`

## 📊 Database Structure

Your database contains these tables:
- `players` - Player information and MVP data
- `alliances` - Alliance information and win counts
- `events` - Event details and scheduling
- `mvp_assignments` - MVP assignments to events
- `winner_assignments` - Alliance winner assignments
- `guide_categories` - Guide category definitions
- `guides` - Guide content and metadata
- `blacklist` - Blacklisted alliances/players

## 🔒 Security Notes

- Always backup your database before making changes
- Keep backup files secure and don't share them publicly
- Consider encrypting backup files for sensitive data
- Test the restore process in a safe environment first

## 📞 Support

If you encounter any issues:
1. Check the error messages carefully
2. Verify file paths and permissions
3. Ensure all required tools are installed
4. Test with a small database first if possible
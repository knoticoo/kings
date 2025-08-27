# King's Choice Management App

A complete web application for managing MVP (Most Valuable Player) and alliance winner assignments for the King's Choice game with fair rotation logic.

## 🎯 Features

- **Fair MVP Rotation**: Ensures all players get MVP before anyone gets it again
- **Alliance Winner Management**: Fair rotation system for alliance victories
- **Modern Web Interface**: Responsive design that works on all devices
- **Real-time Updates**: Live rotation status and dashboard updates
- **Complete CRUD Operations**: Full management of players, alliances, and events
- **Production Ready**: Complete deployment and management tools

## 🚀 Quick Start

### Automatic Installation
```bash
# Clone the repository
git clone <your-repo-url>
cd kings-choice-management

# Run complete installation
./start.sh install

# Start the application
./start.sh start

# Access the app at http://localhost:5000
```

### Manual Installation
```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get install python3 python3-pip python3-venv sqlite3

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Initialize database
python3 -c "from app import create_tables; create_tables()"

# Start application
python3 app.py
```

## 📱 Usage

### Dashboard
- View current MVP and winning alliance
- See statistics and recent events
- Quick access to all management functions

### Player Management
- Add, edit, and delete players
- Assign MVP with automatic rotation enforcement
- Visual indicators for MVP status

### Alliance Management
- Add, edit, and delete alliances
- Assign winners with fair rotation
- Track alliance victory history

### Event Management
- Create and manage game events
- Assign MVP and winners to events
- View detailed event information

## 🔧 Management Commands

```bash
./start.sh install     # Complete setup and installation
./start.sh start       # Start the application
./start.sh stop        # Stop the application
./start.sh restart     # Restart the application
./start.sh status      # Show application status
./start.sh logs [N]    # Show last N lines of logs
./start.sh backup      # Backup the database
./start.sh test        # Run application tests
./start.sh update      # Update dependencies and restart
./start.sh clean       # Clean up temporary files
./start.sh help        # Show help message
```

## 🏗️ Architecture

### Core Components
- **Flask Application**: Modern Python web framework
- **SQLite Database**: Lightweight, reliable data storage
- **Bootstrap UI**: Responsive, mobile-friendly interface
- **Modular Design**: Easy to extend and maintain

### File Structure
```
├── app.py                 # Main application
├── database.py            # Database management
├── models.py              # Data models
├── routes/                # Route handlers
├── utils/                 # Utility functions
├── templates/             # HTML templates
├── static/                # CSS, JS, assets
└── start.sh              # Management script
```

## 🔄 Rotation Logic

### MVP Assignment Rules
1. **First Round**: Any player can be assigned MVP
2. **Subsequent Rounds**: Only assign MVP when all players have been MVP at least once
3. **Fair Distribution**: Players with fewer MVP awards get priority

### Alliance Winner Rules
1. **First Round**: Any alliance can win
2. **Subsequent Rounds**: Only assign winner when all alliances have won at least once
3. **Equal Opportunities**: Alliances with fewer wins get priority

## 📊 Database Schema

### Tables
- **players**: Player information and MVP tracking
- **alliances**: Alliance information and win tracking
- **events**: Game events requiring assignments
- **mvp_assignments**: MVP assignment history
- **winner_assignments**: Alliance winner history

### Relationships
- One MVP per event (enforced by unique constraint)
- One winning alliance per event
- Cascading deletes maintain data integrity

## 🛡️ Security

- **Input Validation**: Server-side validation for all forms
- **SQL Injection Prevention**: SQLAlchemy ORM protection
- **XSS Protection**: Jinja2 template auto-escaping
- **Data Integrity**: Foreign key constraints and transactions

## 📖 Documentation

- **TODO.md**: Comprehensive feature documentation
- **Code Comments**: Every function thoroughly documented
- **API Documentation**: All endpoints explained
- **Setup Guide**: Complete installation instructions

## 🧪 Testing

Run tests to verify functionality:
```bash
./start.sh test
```

Tests include:
- Module import validation
- Database model creation
- Route accessibility
- Rotation logic verification

## 🚀 Production Deployment

### System Requirements
- Python 3.8 or higher
- SQLite3
- 1GB RAM (minimum)
- 100MB disk space

### Performance
- Handles hundreds of concurrent users
- Efficient database queries
- Static file caching
- Production server support (Gunicorn)

### Monitoring
- Application status monitoring
- Log file management
- Database backup system
- Error tracking and recovery

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Update documentation
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the TODO.md for detailed documentation
2. Review the application logs: `./start.sh logs`
3. Verify system status: `./start.sh status`
4. Create an issue in the repository

## 🎮 About King's Choice

This application is designed to manage fair competition in the King's Choice game by ensuring equal opportunities for all players and alliances to receive recognition through the MVP and winner rotation systems.

---

**Ready to manage your King's Choice competitions fairly and efficiently!** 🏆
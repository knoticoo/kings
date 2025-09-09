# King's Choice Discord Bot

A comprehensive Discord bot that provides all the features from the King's Choice web application, designed with a modular architecture for easy maintenance and feature additions.

## 🚀 Features

### Core Management
- **Player Management**: Add, edit, delete players with MVP tracking
- **Alliance Management**: Manage alliances with winner tracking
- **Event Management**: Create and manage game events
- **Fair Rotation Logic**: Ensures fair distribution of MVP and winner assignments

### Content System
- **Guide System**: Categorized guides with search functionality
- **Blacklist Management**: Track blacklisted players and alliances
- **Dashboard**: Real-time overview of current status and statistics

### Advanced Features
- **Slash Commands**: Modern Discord slash command interface
- **Permission System**: Role-based access control
- **Multi-language Support**: English/Russian with auto-translation
- **Comprehensive Logging**: Detailed logging for debugging and monitoring
- **Database Validation**: Built-in database integrity checks
- **Backup System**: Easy database backup creation

## 📁 Project Structure

```
discord/
├── bot.py                 # Main bot file
├── run.py                 # Bot runner script
├── requirements.txt       # Python dependencies
├── .env.example          # Environment configuration template
├── README.md             # This file
├── config/               # Configuration management
│   ├── __init__.py
│   └── settings.py       # Bot settings and configuration
├── core/                 # Core functionality
│   ├── __init__.py
│   ├── database.py       # Database utilities
│   └── rotation.py       # Rotation logic
├── utils/                # Utility functions
│   ├── __init__.py
│   ├── embeds.py         # Discord embed builders
│   └── helpers.py        # Helper functions
└── cogs/                 # Command modules
    ├── __init__.py
    ├── players.py        # Player management commands
    ├── alliances.py      # Alliance management commands
    ├── events.py         # Event management commands
    ├── guides.py         # Guide system commands
    ├── blacklist.py      # Blacklist management commands
    ├── dashboard.py      # Dashboard commands
    ├── admin.py          # Administrative commands
    └── utility.py        # Utility commands
```

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Discord Bot Token
- Access to the King's Choice database

### Setup

1. **Clone or download the bot files**
   ```bash
   # If you have the web app, the discord folder should be in the same directory
   cd /path/to/your/project/discord
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Set up Discord Bot**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application
   - Go to "Bot" section and create a bot
   - Copy the bot token
   - Enable "Message Content Intent" if needed
   - Set up slash commands permissions

5. **Configure database path**
   - Update `DATABASE_PATH` in `.env` to point to your web app's database
   - Default: `../kings_choice.db` (relative to discord folder)

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DISCORD_BOT_TOKEN` | Discord bot token | - | ✅ |
| `DATABASE_PATH` | Path to SQLite database | `kings_choice.db` | ❌ |
| `BOT_PREFIX` | Command prefix | `!kc` | ❌ |
| `ADMIN_ROLE` | Admin role name | `Admin` | ❌ |
| `MODERATOR_ROLE` | Moderator role name | `Moderator` | ❌ |
| `DEFAULT_LANGUAGE` | Default language | `en` | ❌ |
| `AUTO_TRANSLATE` | Enable auto-translation | `true` | ❌ |
| `LOG_LEVEL` | Logging level | `INFO` | ❌ |
| `ENABLE_ROTATION_LOGIC` | Enable rotation logic | `true` | ❌ |
| `ENABLE_AUTO_ANNOUNCEMENTS` | Enable announcements | `true` | ❌ |
| `ENABLE_GUIDE_SYSTEM` | Enable guide system | `true` | ❌ |
| `ENABLE_BLACKLIST` | Enable blacklist | `true` | ❌ |
| `COMMAND_COOLDOWN` | Command cooldown (seconds) | `3` | ❌ |

### Discord Permissions

The bot requires the following permissions:
- Send Messages
- Embed Links
- Use Slash Commands
- Read Message History
- Add Reactions (optional)

## 🚀 Running the Bot

### Method 1: Direct Python
```bash
python run.py
```

### Method 2: Python Module
```bash
python -m bot
```

### Method 3: Background Service
```bash
# Using nohup
nohup python run.py > bot.log 2>&1 &

# Using screen
screen -S discord-bot
python run.py
# Press Ctrl+A, D to detach
```

## 📋 Commands

### Player Management
- `/players` - List all players
- `/addplayer <name>` - Add new player (Admin)
- `/editplayer <id> <new_name>` - Edit player name (Admin)
- `/deleteplayer <id>` - Delete player (Admin)
- `/assignmvp <player_id> <event_id>` - Assign MVP (Admin)
- `/playerinfo <id>` - Get player details
- `/mvpstatus` - Check MVP rotation status

### Alliance Management
- `/alliances` - List all alliances
- `/addalliance <name>` - Add new alliance (Admin)
- `/editalliance <id> <new_name>` - Edit alliance name (Admin)
- `/deletealliance <id>` - Delete alliance (Admin)
- `/assignwinner <alliance_id> <event_id>` - Assign winner (Admin)
- `/allianceinfo <id>` - Get alliance details
- `/winnerstatus` - Check winner rotation status

### Event Management
- `/events [limit]` - List events
- `/addevent <name> [description] [date]` - Add new event (Admin)
- `/editevent <id> <name> [description] [date]` - Edit event (Admin)
- `/deleteevent <id>` - Delete event (Admin)
- `/eventinfo <id>` - Get event details
- `/availableevents [type]` - Get available events

### Guide System
- `/guides [category] [search] [limit]` - List guides
- `/guide <id>` - View specific guide
- `/searchguides <query> [limit]` - Search guides
- `/categories` - List categories
- `/featuredguides [limit]` - Show featured guides

### Blacklist Management
- `/blacklist [limit]` - List blacklist entries
- `/addblacklist [alliance] [player]` - Add to blacklist (Admin)
- `/removeblacklist <id>` - Remove from blacklist (Admin)
- `/searchblacklist <query> [limit]` - Search blacklist
- `/blackliststats` - Show blacklist statistics

### Dashboard & Statistics
- `/dashboard` - Show main dashboard
- `/stats` - Show detailed statistics
- `/rotation` - Show rotation status
- `/current` - Show current MVP/winner

### Administrative
- `/admin` - Show admin panel (Admin)
- `/backup` - Create database backup (Admin)
- `/validate` - Validate database (Admin)
- `/cleanup` - Clean up data (Admin)
- `/reload` - Reload cogs (Admin)
- `/sync` - Sync commands (Admin)

### Utility
- `/help [command]` - Show help information
- `/ping` - Check bot latency
- `/info` - Show bot information
- `/invite` - Get bot invite link

## 🔧 Development

### Adding New Features

1. **Create a new cog** in `cogs/` directory
2. **Follow the existing pattern**:
   - Import required modules
   - Create cog class inheriting from `commands.Cog`
   - Add commands using `@app_commands.command()`
   - Implement `async def setup(bot)` function
3. **Register the cog** in `bot.py` `load_cogs()` method
4. **Test thoroughly** before deploying

### Database Operations

Use the `DatabaseManager` class for all database operations:
```python
from core.database import DatabaseManager

# Execute query
result = await db_manager.execute_query("SELECT * FROM players")

# Execute update
affected = await db_manager.execute_update("UPDATE players SET name = ? WHERE id = ?", (new_name, player_id))
```

### Creating Embeds

Use the `EmbedBuilder` class for consistent embeds:
```python
from utils.embeds import EmbedBuilder

# Success embed
embed = EmbedBuilder.create_success_embed("Success", "Operation completed")

# Error embed
embed = EmbedBuilder.create_error_embed("Error", "Something went wrong")

# Info embed
embed = EmbedBuilder.create_info_embed("Info", "Here's some information")
```

## 🐛 Troubleshooting

### Common Issues

1. **Bot not responding to commands**
   - Check if bot token is correct
   - Verify bot has necessary permissions
   - Ensure slash commands are synced (`/sync`)

2. **Database errors**
   - Verify database path is correct
   - Check if database file exists and is accessible
   - Run `/validate` to check database integrity

3. **Permission errors**
   - Check if user has required role
   - Verify role names in configuration
   - Ensure bot has necessary Discord permissions

4. **Translation errors**
   - Check internet connection
   - Verify `deep-translator` is installed
   - Disable auto-translation if needed

### Logs

Check the `discord_bot.log` file for detailed error information:
```bash
tail -f discord_bot.log
```

## 📝 License

This project is part of the King's Choice Management System and follows the same license terms.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the logs for error details
2. Verify configuration settings
3. Test with minimal setup
4. Create an issue with detailed information

---

**Ready to manage your King's Choice competitions through Discord!** 🏆
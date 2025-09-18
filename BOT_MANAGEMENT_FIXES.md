# Bot Management System Fixes

## Overview
Fixed the bot management system to properly handle per-user bot instances instead of global bot management. Bots are now started/stopped individually when users configure their tokens in the web interface.

## Changes Made

### 1. Install Script (`install_and_start.sh`)
- **Removed automatic bot starting** from the install and start scripts
- Bots are now managed per-user through the web interface settings
- Updated help text to reflect the new behavior
- Main application starts without any bots running globally

### 2. User Bot Manager (`user_bot_manager.py`)
- **Completely rewritten** to properly handle per-user bot instances
- Added proper bot lifecycle management (start/stop/status)
- Added notification functions for MVP and winner announcements
- Added connection testing functionality
- Improved error handling and logging

### 3. User Notifications (`user_notifications.py`)
- **Updated to use bot manager** instead of direct API calls
- Added `ensure_user_bots_running()` function to start bots when needed
- Improved error handling and logging
- Better integration with the bot management system

### 4. Telegram Bot (`telegram_bot.py`)
- **Added user-specific helper functions**
- Added `send_message_to_user()` function for direct user messaging
- Improved error handling and logging
- Better integration with the bot manager

### 5. Discord Bot (`discord_bot.py`)
- **Added user-specific helper functions**
- Added `send_message_to_user()` function for direct user messaging
- Added MVP and winner announcement functions
- Better integration with the bot manager

### 6. User Settings Routes (`routes/user_settings_routes.py`)
- **Updated bot management** to use the new bot manager
- Improved Telegram bot testing with proper connection testing
- Better error handling and user feedback
- Fixed bot starting/stopping logic

### 7. MVP/Winner Assignment Routes
- **Updated to use new notification system**
- `routes/player_routes.py`: MVP assignments now use `send_mvp_announcement()`
- `routes/alliance_routes.py`: Winner assignments now use `send_winner_announcement()`
- Better error handling and logging

## How It Works Now

### 1. User Configuration
- Users go to Settings → Bot Settings in the web interface
- They enter their Telegram bot token and chat ID
- They enter their Discord bot token and channel ID
- They enable/disable bots as needed

### 2. Bot Management
- Bots are started automatically when users enable them in settings
- Bots are stopped when users disable them
- Each user has their own bot instances running independently
- Bot status is tracked and displayed in the interface

### 3. Notifications
- MVP assignments automatically send notifications to user's configured channels
- Winner assignments automatically send notifications to user's configured channels
- Notifications are sent via both Telegram and Discord if configured
- Failed notifications don't break the assignment process

### 4. Testing
- Users can test their bot connections from the settings page
- Test messages are sent to verify configuration
- Connection status is displayed in real-time

## Files Created/Modified

### New Files
- `test_bot_system.py` - Test script for the bot management system
- `start_user_bots.py` - Script to manually start bots for a user
- `BOT_MANAGEMENT_FIXES.md` - This documentation file

### Modified Files
- `install_and_start.sh` - Removed automatic bot starting
- `user_bot_manager.py` - Complete rewrite for per-user management
- `user_notifications.py` - Updated to use bot manager
- `telegram_bot.py` - Added user-specific functions
- `discord_bot.py` - Added user-specific functions
- `routes/user_settings_routes.py` - Updated bot management
- `routes/player_routes.py` - Updated MVP notifications
- `routes/alliance_routes.py` - Updated winner notifications

## Usage

### Starting the Application
```bash
# Install and start (no bots will start automatically)
./install_and_start.sh install
./install_and_start.sh start

# Or just start the app
./install_and_start.sh start-app
```

### Managing User Bots
1. Go to Settings → Bot Settings in the web interface
2. Enter your bot tokens and channel/chat IDs
3. Enable the bots you want to use
4. Test the connections
5. Bots will start automatically when enabled

### Testing Bot System
```bash
# Test the complete bot system
python3 test_bot_system.py

# Start bots for a specific user
python3 start_user_bots.py <user_id>
```

## Benefits

1. **Per-User Management**: Each user manages their own bots independently
2. **No Global Bot Conflicts**: No more conflicts between different users' bot configurations
3. **Better Error Handling**: Improved error handling and user feedback
4. **Automatic Management**: Bots start/stop automatically based on user settings
5. **Better Testing**: Users can test their bot connections before using them
6. **Scalable**: System can handle many users with different bot configurations

## Troubleshooting

### Bot Not Starting
- Check that the bot token is correct
- Check that the chat/channel ID is correct
- Check the logs for error messages
- Use the test function in the web interface

### Notifications Not Working
- Ensure bots are enabled in user settings
- Check that bot tokens are valid
- Verify chat/channel IDs are correct
- Check the logs for error messages

### Database Issues
- The system uses the existing multi-user database
- No additional database changes were needed
- User settings are stored in the existing User model
# 🤖 King's Choice Telegram Bot Setup Guide

## ✅ Your Bot Information
- **Bot Token**: `8228060087:AAEPvgXITQ8avYDDf2dFnh8gtSOdmbbvDTM`
- **Channel ID**: `-1002741248404`
- **Channel Name**: `Kings choice`
- **Channel Username**: `@kingsbotmvp`

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Setup
Your `.env` file has already been created with your bot credentials:
```env
TELEGRAM_BOT_TOKEN=8228060087:AAEPvgXITQ8avYDDf2dFnh8gtSOdmbbvDTM
TELEGRAM_CHANNEL_ID=-1002741248404
TELEGRAM_ENABLED=true
```

### 3. Test Bot Connection
```bash
python3 telegram_bot.py
```

### 4. Start the Web Application
```bash
python3 app.py
```

## 🎯 Features

### Automatic Announcements
The bot will automatically send Russian announcements when you:

1. **Assign MVP to a player**
   - Example: `Добрый вечер команда, MVP за Uncharted Waters достается Aphrodite! Спасибо!`

2. **Assign alliance as winner**
   - Example: `Поздравляем! Победителем события Kingdom War становится альянс Dragons Alliance! Отлично!`

### Manual Messages
- Navigate to `/telegram-message` in your web app
- Write any text in any language
- It will be automatically translated to Russian and sent to your channel

## 📝 Russian Templates

The bot uses 10 different Russian templates for each type of announcement:

### MVP Templates:
1. `"Добрый вечер команда, MVP за {event_name} достается {player_name}! Спасибо!"`
2. `"Привет всем! MVP турнира {event_name} становится {player_name}! Поздравляем!"`
3. `"Команда, объявляем MVP события {event_name} - это {player_name}! Отличная работа!"`
4. `"Доброго времени суток! За отличную игру в {event_name}, MVP получает {player_name}!"`
5. `"Внимание команда! MVP за {event_name} заслуженно достается {player_name}! Браво!"`
6. `"Товарищи! Лучший игрок события {event_name} - {player_name}! Поздравляем с MVP!"`
7. `"Приветствую всех! MVP турнира {event_name} по праву становится {player_name}!"`
8. `"Команда, с гордостью объявляем MVP за {event_name} - {player_name}! Молодец!"`
9. `"Добрый день! За выдающуюся игру в {event_name}, MVP присуждается {player_name}!"`
10. `"Друзья! MVP события {event_name} заслуженно получает {player_name}! Поздравления!"`

### Alliance Winner Templates:
1. `"Поздравляем! Победителем события {event_name} становится альянс {alliance_name}! Отлично!"`
2. `"Команда, объявляем победителя {event_name} - альянс {alliance_name}! Поздравляем!"`
3. `"Внимание всем! Победитель турнира {event_name} - могучий альянс {alliance_name}!"`
4. `"Друзья! За отличную командную работу в {event_name}, побеждает {alliance_name}!"`
5. `"Товарищи! Чемпионом события {event_name} становится альянс {alliance_name}! Браво!"`
6. `"Приветствую! Заслуженную победу в {event_name} одерживает альянс {alliance_name}!"`
7. `"Команда, с радостью объявляем победителя {event_name} - {alliance_name}! Молодцы!"`
8. `"Добрый вечер! Триумфатором турнира {event_name} становится {alliance_name}!"`
9. `"Внимание! За выдающуюся игру в {event_name}, победу празднует {alliance_name}!"`
10. `"Поздравления! Абсолютным чемпионом {event_name} становится альянс {alliance_name}!"`

## 🔧 How It Works

### MVP Assignment Flow:
1. You assign MVP through web interface (`/players/assign-mvp`)
2. Database is updated with MVP assignment
3. **Telegram bot automatically sends Russian announcement**
4. Success message shown in web interface

### Alliance Winner Assignment Flow:
1. You assign winner through web interface (`/alliances/assign-winner`)
2. Database is updated with winner assignment
3. **Telegram bot automatically sends Russian announcement**
4. Success message shown in web interface

### Manual Message Flow:
1. Navigate to `/telegram-message` in web app
2. Enter your message in any language
3. Click "Translate & Send to Telegram"
4. Message is translated to Russian using Google Translate
5. **Russian message sent to Telegram channel**

## 🛠️ Bot Configuration

### Bot Permissions Required:
- Send messages to channel
- Read channel info

### Channel Setup:
1. Add your bot (`@YourBotName`) to the channel as administrator
2. Give it permission to post messages
3. The bot will use channel ID `-1002741248404`

## 📱 Testing

### Test Bot Connection:
```bash
python3 -c "
from telegram_bot import test_bot_connection
success, message = test_bot_connection()
print('✅ Success' if success else '❌ Failed')
print(f'Message: {message}')
"
```

### Test MVP Announcement:
```bash
python3 -c "
from telegram_bot import send_mvp_announcement
send_mvp_announcement('Test Event', 'Test Player')
"
```

### Test Winner Announcement:
```bash
python3 -c "
from telegram_bot import send_winner_announcement
send_winner_announcement('Test Event', 'Test Alliance')
"
```

### Test Manual Message:
```bash
python3 -c "
from telegram_bot import send_manual_message
send_manual_message('This is a test message that will be translated to Russian')
"
```

## 🚨 Troubleshooting

### Common Issues:

1. **Bot can't send messages**
   - Check if bot is added to channel as admin
   - Verify channel ID is correct
   - Ensure bot has posting permissions

2. **Translation not working**
   - Check internet connection
   - Google Translate service might be temporarily unavailable
   - Original text will be sent if translation fails

3. **Environment variables not loaded**
   - Make sure `.env` file exists in project root
   - Check that `python-dotenv` is installed
   - Restart the application after changing `.env`

### Debug Mode:
Enable debug logging by adding to your `.env`:
```env
DEBUG=true
```

## 🎉 Success!

Your Telegram bot is now configured and ready! 

- **Automatic announcements** will be sent when you assign MVP/winners
- **Manual messages** can be sent via the web interface at `/telegram-message`
- **All messages** are automatically translated to Russian
- **10 different templates** ensure variety in announcements

Enjoy your automated King's Choice management system! 🏆
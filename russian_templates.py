"""
Russian announcement templates for King's Choice Telegram bot
Contains various templates for MVP and alliance winner announcements
"""

import random

# MVP Announcement Templates in Russian
MVP_TEMPLATES = [
    "Добрый вечер команда, MVP за {event_name} достается {player_name}! Спасибо!",
    "Привет всем! MVP турнира {event_name} становится {player_name}! Поздравляем!",
    "Команда, объявляем MVP события {event_name} - это {player_name}! Отличная работа!",
    "Доброго времени суток! За отличную игру в {event_name}, MVP получает {player_name}!",
    "Внимание команда! MVP за {event_name} заслуженно достается {player_name}! Браво!",
    "Товарищи! Лучший игрок события {event_name} - {player_name}! Поздравляем с MVP!",
    "Приветствую всех! MVP турнира {event_name} по праву становится {player_name}!",
    "Команда, с гордостью объявляем MVP за {event_name} - {player_name}! Молодец!",
    "Добрый день! За выдающуюся игру в {event_name}, MVP присуждается {player_name}!",
    "Друзья! MVP события {event_name} заслуженно получает {player_name}! Поздравления!"
]

# Alliance Winner Announcement Templates in Russian
WINNER_TEMPLATES = [
    "Поздравляем! Победителем события {event_name} становится альянс {alliance_name}! Отлично!",
    "Команда, объявляем победителя {event_name} - альянс {alliance_name}! Поздравляем!",
    "Внимание всем! Победитель турнира {event_name} - могучий альянс {alliance_name}!",
    "Друзья! За отличную командную работу в {event_name}, побеждает {alliance_name}!",
    "Товарищи! Чемпионом события {event_name} становится альянс {alliance_name}! Браво!",
    "Приветствую! Заслуженную победу в {event_name} одерживает альянс {alliance_name}!",
    "Команда, с радостью объявляем победителя {event_name} - {alliance_name}! Молодцы!",
    "Добрый вечер! Триумфатором турнира {event_name} становится {alliance_name}!",
    "Внимание! За выдающуюся игру в {event_name}, победу празднует {alliance_name}!",
    "Поздравления! Абсолютным чемпионом {event_name} становится альянс {alliance_name}!"
]

def get_random_mvp_template():
    """Get a random MVP announcement template"""
    return random.choice(MVP_TEMPLATES)

def get_random_winner_template():
    """Get a random alliance winner announcement template"""
    return random.choice(WINNER_TEMPLATES)

def format_mvp_announcement(event_name, player_name):
    """Format MVP announcement with random template"""
    template = get_random_mvp_template()
    return template.format(event_name=event_name, player_name=player_name)

def format_winner_announcement(event_name, alliance_name):
    """Format alliance winner announcement with random template"""
    template = get_random_winner_template()
    return template.format(event_name=event_name, alliance_name=alliance_name)

# Example usage and test function
def test_templates():
    """Test function to see how templates look"""
    print("=== MVP Announcement Examples ===")
    for i in range(3):
        print(f"{i+1}. {format_mvp_announcement('Uncharted Waters', 'Aphrodite')}")
    
    print("\n=== Winner Announcement Examples ===")
    for i in range(3):
        print(f"{i+1}. {format_winner_announcement('Kingdom War', 'Dragons Alliance')}")

if __name__ == "__main__":
    test_templates()
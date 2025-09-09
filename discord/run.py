#!/usr/bin/env python3
"""
King's Choice Discord Bot Runner
Main entry point for the Discord bot
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the discord directory to Python path
discord_dir = Path(__file__).parent
sys.path.insert(0, str(discord_dir))

# Import bot
from bot import main

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('discord_bot.log'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting King's Choice Discord Bot...")
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        sys.exit(1)
"""Bot Configuration"""
import logging

from src.bot import DustyBot
from src.cogs import cogs
from src.config import get_config
from src.extensions import db

DefaultConfig = get_config()

def create_bot(config_object=DefaultConfig) -> DustyBot:
    """Create Flask App"""
    bot = DustyBot(config_object)
    bot.set_cogs(cogs)

    # Configure logger
    logging.basicConfig(
        datefmt='%x %X %z',
        format='%(name)s [%(asctime)s] [%(levelname)s] %(message)s',
        level=config_object.LEVEL,
    )

    register_extensions(bot)

    return bot

def register_extensions(bot: DustyBot):
    """Register all extensions"""
    db.init_bot(bot)

__version__ = '0.1.0'

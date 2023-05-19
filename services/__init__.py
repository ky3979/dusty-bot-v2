"""Bot Configuration"""
import logging

from flask import Flask

from services.cogs import cogs
from services.config import get_config
from services.extensions import bot, db, migrate

DefaultConfig = get_config()

def create_app(config_object=DefaultConfig):
    """Create Flask App"""
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Configure logger
    logging.basicConfig(
        datefmt='%x %X %z',
        format='%(name)s [%(asctime)s] [%(levelname)s] %(message)s',
        level=config_object.LEVEL,
    )

    register_extensions(app)

    return app

def register_extensions(app: Flask):
    """Register all extensions"""
    db.init_app(app)
    migrate.init_app(app, db)
    bot.init_app(app, db, cogs)

__version__ = '0.1.0'

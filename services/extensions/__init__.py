"""Extensions"""
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from services.extensions.bot import DustyBot

db = SQLAlchemy()
migrate = Migrate()
bot = DustyBot()

"""SQLAlchemy extension"""
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from src.bot import DustyBot

class SQLAlchemy:
    """
    Integrates SQLAlchemy with the discord bot.
    Handles setting up the engine, connection, and session for each database request
    """

    def __init__(self, bot: DustyBot = None):
        self.Model = SQLModel
        self.engine: AsyncEngine = None
        self.session: sessionmaker[AsyncSession] = None

        if bot is not None:
            self.init_bot(bot)

    def init_bot(self, bot: DustyBot):
        """Initialize the connection engine using the bot config"""
        bot.db = self
        self.engine = create_async_engine(
            url=bot.config.SQLALCHEMY_DATABASE_URI,
            future=True,
            echo=False,
            pool_pre_ping=True,
            pool_use_lifo=True,
            pool_recycle=1800,
            pool_size=10,
            max_overflow=20,
        )
        self.session = sessionmaker(class_=AsyncSession, bind=self.engine, expire_on_commit=False)

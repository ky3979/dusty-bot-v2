"""SQLAlchemy extension"""
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import scoped_session, sessionmaker
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
        self._session: AsyncSession = None

        if bot is not None:
            self.init_bot(bot)

    def init_bot(self, bot: DustyBot):
        """Initialize the connection engine using the bot config"""
        bot.db = self
        self.engine = create_async_engine(url=bot.config.SQLALCHEMY_DATABASE_URI, echo=True)
        self._session = self._make_scoped_session(self.engine)

    async def get_session(self) -> AsyncSession:
        """Get session instance"""
        async with self._session() as session:
            return session

    def _make_scoped_session(self, engine: AsyncEngine) -> scoped_session:
        """Create and return a Async Session scoped session"""
        factory = self._make_session_factory(engine)
        return scoped_session(factory)

    def _make_session_factory(self, engine: AsyncEngine) -> sessionmaker:
        """Create and return a Async session maker"""
        return sessionmaker(class_=AsyncSession, bind=engine, expire_on_commit=False)

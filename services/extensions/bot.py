"""Extension object for discord bot"""
import logging
import traceback
from logging import Formatter, LogRecord, handlers

from aiohttp import ClientSession
from discord import Activity, ActivityType, Guild, HTTPException, Intents, InvalidData, NotFound, TextChannel
from discord.ext.commands import Bot, ExtensionFailed, ExtensionNotFound, NoEntryPointError
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from services.exceptions.bot import MissingBotTokenException
from services.exceptions.cog import LoadCogException

class CustomFormatter(Formatter):
    def format(self, record: LogRecord) -> str:
        s = super().format(record)
        return s

PREFIX = '!'
DESCRIPTION = 'Official Dusty Server Bot'

_log = logging.getLogger('DustyBot')

class DustyBot(Bot):
    """
    Dusty Bot object
    """

    def __init__(self, app: Flask = None, db: SQLAlchemy = None, cogs: list[str] = None):
        super().__init__(
            command_prefix=PREFIX,
            description=DESCRIPTION,
            intents=Intents.all()
        )

        self._cogs: list[str] = []
        self.app: Flask = app
        self.token: str = None
        self.ready: bool = False
        self.db: SQLAlchemy = None
        self.my_guild: Guild = None
        self.main_channel: TextChannel = None
        self.session: ClientSession = None
        self.config = None

        if app is not None:
            self.init_app(app, db, cogs)

    def init_app(self, app: Flask, db: SQLAlchemy, cogs: list[str]):
        if 'dusty-bot' in app.extensions:
            raise RuntimeError(
                'A \'Dusty Bot\' instance has already been registered on this Flask app.'
                'Import and use that instance instead.'
            )
        app.extensions['dusty-bot'] = self

        self.app = app
        self.db = db
        self._cogs = cogs
        self.config = app.config

        self.token = app.config['DISCORD_BOT_TOKEN']
        if not self.token:
            raise MissingBotTokenException()

    def run(self):
        """Run the bot"""
        if not self.token:
            raise MissingBotTokenException()

        handler = handlers.RotatingFileHandler(
            filename=self.config['DISCORD_LOG_FILE_PATH'],
            encoding='utf-8',
            maxBytes=32 * 1024 * 1024,  # 32 MiB
            backupCount=5,  # Rotate through 5 files
        )
        formatter = Formatter(
            fmt='%(name)s [%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%x %X %z'
        )
        super().run(
            token=self.token,
            reconnect=True,
            log_handler=handler,
            log_formatter=formatter,
            log_level=self.config['LEVEL']
        )

    async def load_cogs(self):
        """Load the cogs in the cogs folder"""
        for ext in self._cogs:
            try:
                await self.load_extension(ext)
            except (ExtensionNotFound, NoEntryPointError, ExtensionFailed) as e:
                raise LoadCogException(ext) from e

    async def on_ready(self):
        await self.tree.sync()
        if not self.ready:
            self.ready = True
            await self.change_presence(
                activity=Activity(
                    type=ActivityType.watching,
                    name='You sleep.'
                )
            )
            _log.info(
                '\n========================================================\n'
                '\n\tDUSTY BOT IS READY !\n'
                '\tLOGGED IN AS %s !\n'
                '\n========================================================\n',
                str(self.user)
            )

    async def setup_hook(self):
        if self.session is None:
            self.session = ClientSession()

        try:
            guild_id = self.config['DISCORD_GUILD_ID']
            self.my_guild = await self.fetch_guild(int(guild_id))
        except HTTPException:
            _log.error('Error fetching guild with ID %s.', guild_id)
            traceback.print_stack()

        try:
            channel_id = self.config['DISCORD_MAIN_CHANNEL_ID']
            self.main_channel = await self.fetch_channel(int(channel_id))
        except (HTTPException, InvalidData, NotFound):
            _log.error('Error fetching channel with ID %s.', channel_id)
            traceback.print_stack()

        try:
            self.owner_id = int(self.config['DISCORD_OWNER_ID'])
        except ValueError:
            app_info = await self.application_info()
            self.owner_id = app_info.owner.id

        await self.load_cogs()

    async def close(self):
        if self.session is not None:
            await self.session.close()
        await super().close()
        _log.info(
            '\n========================================================\n'
            '\n\tDUSTY BOT IS OFFLINE !\n'
            '\nLOGGED OUT AS %s !\n'
            '\n========================================================\n',
            str(self.user)
        )

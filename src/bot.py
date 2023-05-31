"""Discord bot"""
import logging
import traceback
from logging import Formatter

from discord import Activity, ActivityType, Guild, HTTPException, Intents, InvalidData, NotFound, TextChannel
from discord.ext.commands import Bot, ExtensionFailed, ExtensionNotFound, NoEntryPointError

from src.config import Config
from src.exceptions.bot import MissingBotTokenException
from src.exceptions.cog import LoadCogException


class DustyBot(Bot):
    """
    Dusty Bot object
    """

    def __init__(self, config: Config):
        super().__init__(
            command_prefix=config.DISCORD_COMMAND_PREFIX,
            description=config.DISCORD_BOT_DESCRIPTION,
            intents=Intents.all()
        )

        self.config = config
        self.token: str = config.DISCORD_BOT_TOKEN
        self.ready: bool = False
        self.my_guild: Guild = None
        self.main_channel: TextChannel = None
        self.db = None
        self._cogs: list[str] = []
        self._log = logging.getLogger('DustyBot')

        if not self.token:
            raise MissingBotTokenException()

    def set_cogs(self, cogs: list[str]):
        """Set the bot cogs to load when it runs"""
        self._cogs = cogs

    def run(self):
        """Run the bot"""
        if not self.token:
            raise MissingBotTokenException()

        formatter = Formatter(
            fmt='%(name)s [%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%x %X %z'
        )
        super().run(
            token=self.token,
            reconnect=True,
            log_formatter=formatter,
            log_level=logging.INFO
        )

    async def load_cogs(self):
        """Load the cogs in the cogs folder"""
        for ext in self._cogs:
            try:
                await self.load_extension(ext)
            except (ExtensionNotFound, NoEntryPointError, ExtensionFailed) as e:
                raise LoadCogException(ext) from e

    async def on_ready(self):
        if not self.ready:
            self.ready = True
            await self.change_presence(
                activity=Activity(
                    type=ActivityType.watching,
                    name='You Sleep.'
                )
            )
            self._log.info(
                '\n========================================================\n'
                '\n\tDUSTY BOT IS READY !\n'
                '\tLOGGED IN AS %s !\n'
                '\n========================================================\n',
                str(self.user)
            )

    async def setup_hook(self):
        try:
            guild_id = self.config.DISCORD_GUILD_ID
            self.my_guild = await self.fetch_guild(int(guild_id))
        except HTTPException as e:
            self._log.error('Error fetching guild with ID %s.', guild_id)
            traceback.print_exception(e)

        try:
            channel_id = self.config.DISCORD_MAIN_CHANNEL_ID
            self.main_channel = await self.fetch_channel(int(channel_id))
        except (HTTPException, InvalidData, NotFound) as e:
            self._log.error('Error fetching channel with ID %s.', channel_id)
            traceback.print_exception(e)

        try:
            self.owner_id = int(self.config.DISCORD_OWNER_ID)
        except ValueError:
            app_info = await self.application_info()
            self.owner_id = app_info.owner.id

        await self.load_cogs()
        await self.tree.sync()

    async def close(self):
        await self.db.engine.dispose()
        await super().close()
        self._log.info(
            '\n========================================================\n'
            '\n\tDUSTY BOT IS OFFLINE !\n'
            '\nLOGGED OUT AS %s !\n'
            '\n========================================================\n',
            str(self.user)
        )

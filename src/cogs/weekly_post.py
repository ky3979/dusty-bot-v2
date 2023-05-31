"""Weekend posts task cog"""
import asyncio
import logging
from datetime import datetime, timedelta

from discord import Interaction, app_commands
from discord.ext import commands, tasks

from src.bot import DustyBot
from src.models.weekly_post import WeeklyPost
from src.util.date_util import ceil_datetime, seconds_until
from src.util.logger import log_app_command
from src.exceptions.database import DatabaseException


class WeeklyPostCog(commands.Cog):
    """
    Class to create tasks for sending scheduled posts
    """

    def __init__(self, bot: DustyBot):
        self.bot = bot
        self._log = logging.getLogger('WeeklyPostCog')
        self.syncing_time = False
        self.send_posts.start() # pylint: disable=no-member

    @tasks.loop(minutes=30)
    async def send_posts(self):
        """Send posts from database on their scheduled day and time"""
        self._log.info('[send_post] Executing send_posts task.')
        now = datetime.now()

        try:
            posts_for_today = await WeeklyPost.get_by_day_of_week(now.weekday())
        except DatabaseException:
            self._log.error('There was an error getting the weekly posts.')
            posts_for_today = []

        self._log.info('[send_post] Got %d posts for weekday %d.', len(posts_for_today), now.weekday())
        self._log.info('[send_post] Sending posts with hour %d and minute %d.', now.hour, now.minute)

        for post in posts_for_today:
            self._log.info('[send_post] Got post ID %d with hour %d and minute %d.', post.id, post.hour, post.minute)
            if post.hour == now.hour and post.minute == now.minute:
                self._log.info('[send_post] Sending post ID %d.', post.id)
                await self.bot.main_channel.send(post.content)
                self._log.info('[send_post] Post ID %d successfully sent.', post.id)

    @send_posts.before_loop
    async def before_send_posts(self):
        """Sleep until task is either at minute 0 or 30"""
        self._log.info('[before_send_posts] Start before_send_posts.')
        await self.bot.wait_until_ready()

        now = datetime.now()
        if now.minute in [0, 30]:
            # Task is synced to half hour starting at 0
            return

        self.syncing_time = True
        while self.syncing_time:
            # Wait until next half hour
            next_half_hour = ceil_datetime(now, timedelta(minutes=30))
            delay = seconds_until(next_half_hour.hour, next_half_hour.minute)

            self._log.info('[before_send_posts] Sleeping until hour %d and minute %d.',
                           next_half_hour.hour, next_half_hour.minute)
            await asyncio.sleep(delay)
            self._log.info('[before_send_posts] End before_send_posts.')
            self.syncing_time = False

    @app_commands.command(name='addwp')
    async def add_weekly_post(
        self,
        interaction: Interaction,
        content: str,
        day_of_week: int,
        hour: int,
        minute: int
    ): # pylint: disable=too-many-arguments
        """Add a new weekly post

        Add a weekly post that will be sent on a
        given day of week, hour, and minute where the minutes
        are half hour intervals (30 minutes)

        Args:
            content (str): Content of post
            day_of_week (int): What day of the week to send post (MONDAY = 0,... , SUNDAY = 6)
            hour (int): What UTC hour of the day to send post
            minute (int): What minute of the day to send post (0 or 30)
        """
        log_app_command(self._log, interaction)
        self._log.info('Creating new WeeklyPost for weekday %d, hour %d, and minute %d.',
                       day_of_week, hour, minute)
        await interaction.response.defer()

        try:
            post = await WeeklyPost.create(
                content=content,
                day_of_week=day_of_week,
                hour=hour,
                minute=minute
            )
            self._log.info('Successfully created WeeklyPost with ID %d', post.id)
            await interaction.followup.send('Your weekly post was successfully created!')
        except DatabaseException:
            self._log.error('Error creating WeeklyPost for weekday %d, hour %d, and minute %d.',
                            day_of_week, hour, minute)
            await interaction.followup.send('There was an error creating your new post.')

async def setup(bot: DustyBot):
    await bot.add_cog(WeeklyPostCog(bot))
    
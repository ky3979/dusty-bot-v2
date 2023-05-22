"""Weekend posts task cog"""
import asyncio
import logging
import traceback
from datetime import datetime, timedelta

from discord import Interaction, app_commands
from discord.ext import commands, tasks

from services.extensions.bot import DustyBot
from services.models.weekly_post import WeeklyPost
from services.util.date_util import ceil_datetime, seconds_until
from services.util.logger import log_app_command

_log = logging.getLogger('WeeklyPostCog')

class WeeklyPostCog(commands.Cog):
    """
    Class to create tasks for sending scheduled posts
    """

    def __init__(self, bot: DustyBot):
        self.bot = bot
        self.syncing_time = False
        self.send_posts.start()

    @tasks.loop(minutes=30)
    async def send_posts(self):
        """Send posts from database on their scheduled day and time"""
        _log.info(f'[send_post] Executing send_posts task.')
        now = datetime.now()

        try:
            posts_for_today = WeeklyPost.get_by_day_of_week(now.weekday())
        except:
            _log.error('There was an error getting the weekly posts.')
            traceback.print_stack()
            posts_for_today = []
    
        _log.info(f'[send_post] Got {len(posts_for_today)} posts for {now}.')
        _log.info(f'[send_post] Sending posts with hour {now.hour} and minute {now.minute}.')
        
        for post in posts_for_today:
            _log.info(f'[send_post] Got post {post.id} with hour {post.hour} and minute {post.minute}.')
            if post.hour == now.hour and post.minute == now.minute:
                _log.info(f'[send_post] Sending post {post.id}.')
                await self.bot.main_channel.send(post.content)
                _log.info(f'[send_post] Post {post.id} successfully sent.')

    @send_posts.before_loop
    async def before_send_posts(self):
        """Sleep until task is either at minute 0 or 30"""
        _log.info(f'[send_post] Before send_posts task.')
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

            _log.info(f'[send_post] Sleep at {now}.')
            await asyncio.sleep(delay)
            now = datetime.now()
            _log.info(f'[send_post] Resume at {now}.')
            self.syncing_time = False

    @app_commands.command(name='addwp')
    async def add_weekly_post(
        self, 
        interaction: Interaction,
        content: str,
        day_of_week: int,
        hour: int,
        minute: int
    ):
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
        log_app_command(_log, 'add_weekly_post', interaction)
        _log.info(f'Creating new WeeklyPost for day {day_of_week}, hour {hour}, and minute {minute}.')
        await interaction.response.defer()

        try:
            WeeklyPost.create(
                content=content,
                day_of_week=day_of_week,
                hour=hour,
                minute=minute
            )
        except ValueError:
            await interaction.followup.send('minute must be 0 or 30.')
        except Exception:
            _log.error(f'Error creating WeeklyPost for day {day_of_week}, hour {hour}, and minute {minute}.')
            traceback.print_stack()
            await interaction.followup.send('There was an error saving your new post.')
        await interaction.followup.send('Your weekly post was successfully created!')

async def setup(bot: DustyBot):
    await bot.add_cog(WeeklyPostCog(bot))
    
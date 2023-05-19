"""Logger util"""
from logging import Logger

from discord import Interaction


def log_app_command(log: Logger , command: str, interaction: Interaction):
    """Log who enter the given application command"""
    user = interaction.user.name
    log.info(f'User {user} excuted command {command}.')

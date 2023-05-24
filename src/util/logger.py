"""Logger util"""
from logging import Logger

from discord import Interaction


def log_app_command(log: Logger, interaction: Interaction):
    """Log who enter the given application command"""
    user = interaction.user.name
    command = interaction.command.name
    log.info('User %s excuted command %s.', user, command)

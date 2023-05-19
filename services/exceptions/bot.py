"""Base Bot Exceptions"""

class MissingBotTokenException(Exception):
    """Missing bot token in config exception"""
    def __init__(self):
        super().__init__('\'DISCORD_BOT_TOKEN\' must be set.')

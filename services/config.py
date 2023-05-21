"""Config objects to hold project level configuration"""
# pylint: disable=no-member
import logging
import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
    has_dotenv = True
except ImportError:
    has_dotenv = False

@dataclass
class Config:
    """Base config object"""
    if has_dotenv:
        load_dotenv() # Take environment variables from .env
    ENV: str = None
    DEBUG: bool = False
    LEVEL: int = logging.INFO

    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_DATABASE_URI: str = 'sqlite:///'
    SQLALCHEMY_LOG_LEVEL: int = logging.INFO

    DISCORD_BOT_TOKEN: str = os.getenv('DISCORD_BOT_TOKEN', '')
    DISCORD_GUILD_ID: str = os.getenv('DISCORD_GUILD_ID', '')
    DISCORD_OWNER_ID: str = os.getenv('DISCORD_OWNER_ID', '')
    DISCORD_MAIN_CHANNEL_ID: str = os.getenv('DISCORD_MAIN_CHANNEL_ID', '')

@dataclass
class ProdConfig(Config):
    """Production config object"""
    ENV: str = 'prod'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', '')

@dataclass
class LocalConfig(Config):
    """Local config object"""
    ENV: str = 'local'
    DEBUG: bool = True
    LEVEL: int = logging.DEBUG
    DB_USER: str = 'dusty'
    DB_PASSWORD: str = 'dusty'
    DB_SCHEMA: str = 'dusty'
    SQLALCHEMY_DATABASE_URI: str = f'postgresql://{DB_USER}:{DB_PASSWORD}@localhost:5432/{DB_SCHEMA}'

def get_config(name=os.getenv('CONFIG', 'local')):
    """Retrieve a config"""
    for config in Config.__subclasses__():
        if config.ENV == name:
            return config

    raise Exception(f'Requested configuration "{name}" was not found')

"""Cog Exceptions"""
from .dusty_exception import DustyException

class LoadCogException(DustyException):
    """Loading cog exception"""
    def __init__(self, ext: str):
        super().__init__(f'Failed to load extension \'{ext}\'')

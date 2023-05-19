"""Cog Exceptions"""

class LoadCogException(Exception):
    """Loading cog exception"""
    def __init__(self, ext: str):
        super().__init__(f'Failed to load extension \'{ext}\'')

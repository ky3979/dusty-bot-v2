"""Database Exceptions"""
from .dusty_exception import DustyException

class DatabaseException(DustyException):
    """Database exception"""
    def __init__(self):
        super().__init__('Error with the database session.')

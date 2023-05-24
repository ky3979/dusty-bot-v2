"""Base exception"""
import traceback

class DustyException(Exception):
    """Base exception for dusty bot"""
    def __init__(self, *args: object):
        super().__init__(*args)
        traceback.print_exception(self)

"""Scheduled post model"""
from typing import Type, TypeVar

from sqlalchemy import Column, Integer, String
from sqlalchemy.event import listens_for

from services.database import BaseModel

T = TypeVar('T', bound='WeeklyPost')

class WeeklyPost(BaseModel):
    """
    Post to be sent weekly
    """

    __tablename__ = 'weekly_post'

    content = Column(String, nullable=False)
    day_of_week = Column(Integer, nullable=False)
    hour = Column(Integer, nullable=False)
    minute = Column(Integer, server_default='0')

    @classmethod
    def get_by_day_of_week(cls: Type[T], day_of_week: int) -> list[T]:
        return cls.query.filter_by(day_of_week=day_of_week).all()

@listens_for(WeeklyPost.minute, 'set')
def before_set_minute(_, value, __, ___):
    if value not in [0, 30]:
        raise ValueError('[minute] must be 0 or 30')

"""Weekly post model"""
from typing import Type, TypeVar

from sqlalchemy.future import select
from sqlmodel import Field

from src.extensions import db
from src.models.mixins import DustyModel

T = TypeVar('T', bound='WeeklyPost')

class WeeklyPost(DustyModel, table=True):
    """
    Post to be sent weekly
    """
    __tablename__ = 'weekly_post'

    content: str
    day_of_week: int
    hour: int
    minute: int = Field(default=0)

    @classmethod
    async def get(cls: Type[T], **kwargs) -> list[T]:
        async with db.session() as session:
            stmt = select(cls).filter_by(**kwargs)
            result = await session.execute(stmt)
            return result.scalars().all()

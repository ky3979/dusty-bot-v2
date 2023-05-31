"""Database mixins"""
from __future__ import annotations

from datetime import datetime
from typing import Optional, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import Column, DateTime, func
from sqlmodel import Field

from src.extensions import db


class TimeStampMixin(BaseModel):
    """
    Mixin to provide date information to models
    """
    created_at: Optional[datetime] = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        )
    )

    updated_at: Optional[datetime] = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
        )
    )

_T = TypeVar('_T')

class CRUDMixin(BaseModel):
    """
    Mixin to provide CRUD operations to models
    """

    @classmethod
    async def create(cls: Type[_T], commit: bool=True,**kwargs) -> _T:
        """Create model"""
        instance = cls(**kwargs)
        return await instance.save(commit=commit)

    async def update(self, commit: bool=True, **kwargs):
        """Update model"""
        kwargs.pop('id', None)
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return await self.save(commit=commit) if commit else self

    async def save(self, commit: bool=True):
        """Save model"""
        session = await db.get_session()
        session.add(self)
        if commit:
            await session.commit()
        return self

    async def delete(self, commit: bool=True):
        """Delete model"""
        session = await db.get_session()
        session.delete(self)
        return commit and await session.commit()
        
T = TypeVar('T', bound='DustyModel')

class DustyModel(db.Model, CRUDMixin, TimeStampMixin):
    """
    Base model for dusty bot database models
    """

    __abstract__ = True

    id: Optional[int] = Field(default=None, primary_key=True)

    @classmethod
    async def get(cls: Type[T], id: int) -> T:
        """Return object by id"""
        session = await db.get_session()
        model = await session.get(cls, id)
        return model

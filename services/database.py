"""Database mixins"""
from typing import Type, TypeVar

from sqlalchemy import Column, Integer

from services.extensions import db

_T = TypeVar("_T")

class CRUDMixin():
    """
    Mixin to provide CRUD operations to models
    """

    @classmethod
    def create(cls: Type[_T], commit: bool=True, **kwargs) -> _T:
        """Create model"""
        instance = cls(**kwargs) # type: ignore[call-arg]
        return instance.save(commit=commit) # type: ignore[attr-defined]

    def update(self, commit: bool=True, **kwargs):
        """Update model"""
        kwargs.pop('id', None)
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return self.save(commit=commit) if commit else self

    def save(self, commit: bool=True):
        """Save model"""
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit: bool=True):
        """Delete model"""
        db.session.delete(self)
        return commit and db.session.commit()


T = TypeVar('T', bound='BaseModel')

class BaseModel(db.Model, CRUDMixin):
    """
    Base model for database models
    """

    __abstract__ = True

    id = Column(Integer, primary_key=True)

    @classmethod
    def get(cls: Type[T], _id: int) -> T:
        """Return object by id"""
        return cls.query.filter_by(id=_id).one()

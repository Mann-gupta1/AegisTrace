"""Declarative base only — safe to import from Alembic without creating an async engine."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass

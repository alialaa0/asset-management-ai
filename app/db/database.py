"""
Database configuration.

This module is responsible for:
- Loading environment variables
- Creating the SQLAlchemy engine
- Providing database sessions
- Defining the declarative base class
"""

from typing import Generator
import os

from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Session,
    sessionmaker,
)

# ---------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError("DATABASE_URL environment variable is not set.")


# ---------------------------------------------------------------------
# Database Engine
# ---------------------------------------------------------------------

engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
)


# ---------------------------------------------------------------------
# Session Factory
# ---------------------------------------------------------------------

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


# ---------------------------------------------------------------------
# Base Class
# ---------------------------------------------------------------------

class Base(DeclarativeBase):
    """
    Base class for all ORM models.
    """

    pass


# ---------------------------------------------------------------------
# Dependency
# ---------------------------------------------------------------------

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides
    a database session per request.
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
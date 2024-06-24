import enum
from sqlalchemy import create_engine

from sqlalchemy.orm import declarative_base, sessionmaker
from alembic import config

SQLALCHEMY_DATABASE_URL = "sqlite:////Users/vinay/Documents/stream/rmonitoring/chomb.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
metadata = Base.metadata

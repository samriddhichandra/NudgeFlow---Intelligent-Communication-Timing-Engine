from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

is_sqlite = settings.database_url.startswith("sqlite")
engine = create_engine(
    settings.database_url,
    pool_pre_ping=not is_sqlite,
    connect_args={"check_same_thread": False} if is_sqlite else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def initialize_temporary_database():
    """Create the ephemeral Vercel SQLite schema when no managed DB exists."""
    if settings.uses_temporary_vercel_database:
        # Models are imported by the application before startup, so their table
        # metadata is registered on Base by the time this runs.
        Base.metadata.create_all(bind=engine)

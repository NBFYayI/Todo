import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Use DATABASE_URL env var if provided, otherwise default to local Postgres.
SQLALCHEMY_DATABASE_URL: str = "postgresql+psycopg://todo_user:1222@localhost:5432/tododb"

# Create engine; pool_pre_ping keeps connections alive.
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Yield a database session for dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Import all models and create tables. Call once at startup."""
    import app.models  # noqa: F401 - ensure models are registered with Base

    Base.metadata.create_all(bind=engine)


def reset_db() -> None:
    """Drop all tables and recreate them. Use for development only."""
    import app.models  # noqa: F401 - ensure models are registered with Base
    
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine) 
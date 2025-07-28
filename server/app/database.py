import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Use asyncpg for async PostgreSQL connection
SQLALCHEMY_DATABASE_URL: str = "postgresql+asyncpg://todo_user:1222@localhost:5432/tododb"

# Create async engine
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

Base = declarative_base()


async def get_db():
    """Yield an async database session for dependency injection."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Import all models and create tables. Call once at startup."""
    import app.models  # noqa: F401 - ensure models are registered with Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def reset_db() -> None:
    """Drop all tables and recreate them. Use for development only."""
    import app.models  # noqa: F401 - ensure models are registered with Base
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all) 
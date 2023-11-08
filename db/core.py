from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

# Set up the synchronous database engine
engine = create_async_engine(settings.sqlalchemy_database_url, echo=True)

# Set up the asynchronous session
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Set up the synchronous database engine
engine_sync = create_engine(settings.sqlalchemy_sync_database_url, echo=True)

# Set up the synchronous session
SessionLocal = sessionmaker(engine_sync, expire_on_commit=False)


# Dependency to get the async database session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# Dependency to get the sync database session
def get_sync_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

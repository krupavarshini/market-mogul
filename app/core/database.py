# app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# Handle both SQLite and PostgreSQL
database_url = settings.DATABASE_URL

if database_url.startswith("postgres"):
    # Ensure async driver
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(database_url, echo=False)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with async_session_maker() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
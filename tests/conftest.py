import sys
import os
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import pytest_asyncio

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from main import app
from app.models import Base
from app.depends import get_db


# SQLite test database
DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(DATABASE_URL)

TestingSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# Override DB dependency
async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


# Create and drop tables for tests
@pytest_asyncio.fixture(scope="function", autouse=True)
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Test client
@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)  # Direct in-memory FastAPI app transport

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine

from vpnBot.config import DATABASE_URL
from vpnBot.db.tables import *


class EngineManager:
    def __init__(self, path: str) -> None:
        self.path = path

    async def __aenter__(self) -> AsyncEngine:
        self.engine = create_async_engine(self.path, echo=True)
        return self.engine

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.engine.dispose()


class DBManager:
    def __init__(self):
        self.session_maker = None
        asyncio.run(self._init())

    async def _init(self):
        async with EngineManager(DATABASE_URL) as engine:
            self.session_maker = async_sessionmaker(engine, expire_on_commit=False)
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

    async def get_user_by_id(self, user_id: int) -> User:
        # noinspection PyTypeChecker
        query = select(User).where(User.id == user_id)
        async with self.session_maker() as session:
            result = await session.execute(query)
            user = result.scalars().first()
            return user

    async def add_record(self, model: Base, **kwargs) -> Base:
        new_record = model(**kwargs)
        async with self.session_maker() as session:
            session.add(new_record)
            await session.commit()
            return new_record

    async def get_user_devices(self, user_id: int) -> list[Client]:
        # noinspection PyTypeChecker
        query = select(Client).where(Client.user_id == user_id)
        async with self.session_maker() as session:
            result = await session.execute(query)
            clients = result.scalars()
            return clients.all()


db_manager = DBManager()

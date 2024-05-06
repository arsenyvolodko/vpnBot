import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine

from vpnBot.config import DATABASE_URL
from vpnBot.db.tables import *
from vpnBot.enums.operation_type_enum import OperationTypeEnum
from vpnBot.utils.keys_util import generate_keys

from vpnBot.exceptions.devices_limit_error import DevicesLimitError
from vpnBot.exceptions.no_available_ips_error import NoAvailableIpsError
from vpnBot.exceptions.not_enough_money_error import NotEnoughMoneyError
from vpnBot.static.common import DEVICES_MAX_AMOUNT


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

    async def get_user_by_id(self, user_id: int) -> User | None:
        # noinspection PyTypeChecker
        query = select(User).where(User.id == user_id)
        async with self.session_maker() as session:
            result = await session.execute(query)
            user = result.scalars().first()
            return user

    async def add_record(self, new_record) -> Base:
        async with self.session_maker() as session:
            async with session.begin():
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

    async def update_balance(self, session, user_id: int, amount: int, op_type: OperationTypeEnum) -> bool:
        # noinspection PyTypeChecker
        query = select(User).where(User.id == user_id).with_for_update()
        result = await session.execute(query)
        user = result.scalars().first()

        if op_type == OperationTypeEnum.DECREASE:
            if user.balance < amount:
                return False
            user.balance -= amount
        else:
            user.balance += amount
        # session.add(user)  # todo ??
        return True

    async def add_client(self, new_client: Client):
        async with self.session_maker() as session:
            async with session.begin():
                # noinspection PyTypeChecker
                devices_query = select(Client).where(
                    Client.user_id == new_client.user_id
                ).with_for_update()

                devices = await session.execute(devices_query).scalars().all()
                if len(devices) == DEVICES_MAX_AMOUNT:
                    raise DevicesLimitError()

                balance_updated = await self.update_balance(
                    session, new_client.user_id,
                    amount=PRICE, op_type=OperationTypeEnum.DECREASE
                )
                if not balance_updated:
                    raise NotEnoughMoneyError()

                ips_query = select(Ips).where(
                    Ips.client_id is None
                ).with_for_update()

                ips = await session.execute(ips_query).scalars().first()
                if not ips:
                    raise NoAvailableIpsError()
                ips.client_id = new_client.id

                session.add(new_client)
                await session.commit()
                return new_client


db_manager = DBManager()

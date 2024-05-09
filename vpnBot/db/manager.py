import asyncio

from sqlalchemy import select, func, null, desc
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine

from vpnBot.config import DATABASE_URL
from vpnBot.db.tables import *
from vpnBot.enums.operation_type_enum import OperationTypeEnum

from vpnBot.exceptions.devices_limit_error import DevicesLimitError
from vpnBot.exceptions.no_available_ips_error import NoAvailableIpsError
from vpnBot.exceptions.not_enough_money_error import NotEnoughMoneyError
from vpnBot.static.common import *
from vpnBot.utils.date_util import get_next_date


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

    # async def get_user_by_id(self, user_id: int) -> User | None:
    #     async with self.session_maker() as session:
    #         # noinspection PyTypeChecker
    #         query = select(User).where(User.id == user_id)
    #         result = await session.execute(query)
    #         user = result.scalars().first()
    #         return user

    async def add_record(self, new_record) -> Base:
        async with self.session_maker() as session:
            async with session.begin():
                session.add(new_record)
                await session.commit()
                return new_record

    async def get_record(self, model, record_id: int):
        async with self.session_maker() as session:
            # noinspection PyTypeChecker
            query = select(model).where(model.id == record_id)
            result = await session.execute(query)
            record = result.scalars().first()
            return record

    async def delete_record(self, record):
        async with self.session_maker() as session:
            async with session.begin():
                session.delete(record)
                await session.commit()

    async def get_user_devices(self, user_id: int) -> list[Client]:
        async with self.session_maker() as session:
            # noinspection PyTypeChecker
            query = select(Client).where(Client.user_id == user_id)
            result = await session.execute(query)
            clients = result.scalars()
            return clients.all()

    async def get_ips_by_client_id(self, client_id: int) -> Ips | None:
        async with self.session_maker() as session:
            query = select(Ips).where(Ips.client_id == client_id)
            result = await session.execute(query)
            ips = result.scalars()  # todo maybe inline
            return ips.first()

    async def get_keys_by_client_id(self, client_id: int) -> Keys | None:
        async with self.session_maker() as session:
            query = select(Keys).join(Client).where(Client.id == client_id)
            result = await session.execute(query)
            keys = result.scalars()  # todo maybe inline
            return keys.first()

    async def add_transaction(
        self,
        session,
        user_id: int,
        value: int,
        op_type: OperationTypeEnum,
        comment: TransactionCommentEnum,
    ):
        new_transaction = Transaction(
            user_id=user_id, value=value, operation_type=op_type, comment=comment
        )

        session.add(new_transaction)

    async def update_balance(
        self,
        session,
        user_id: int,
        value: int,
        op_type: OperationTypeEnum,
        comment: TransactionCommentEnum,
    ) -> bool:
        # noinspection PyTypeChecker
        query = select(User).where(User.id == user_id).with_for_update()
        result = await session.execute(query)
        user = result.scalars().first()

        if op_type == OperationTypeEnum.DECREASE:
            if user.balance < value:
                return False
            user.balance -= value
        else:
            user.balance += value
        await self.add_transaction(
            session, user_id=user_id, value=value, op_type=op_type, comment=comment
        )
        return True

    async def add_client(self, user_id: int):
        async with self.session_maker() as session:
            async with session.begin():
                # noinspection PyTypeChecker
                devices_query = (
                    select(Client)
                    .where(Client.user_id == user_id)
                    .order_by(desc(Client.device_num))
                )
                devices_result = await session.execute(devices_query)
                devices_num = devices_result.scalars().first().device_num
                if devices_num == DEVICES_MAX_AMOUNT:
                    raise DevicesLimitError()

                balance_updated = await self.update_balance(
                    session,
                    user_id,
                    value=PRICE,
                    op_type=OperationTypeEnum.DECREASE,
                    comment=TransactionCommentEnum.ADD_DEVICE,
                )
                if not balance_updated:
                    raise NotEnoughMoneyError()

                ips_query = select(Ips).where(Ips.client_id == null()).with_for_update()
                ips_result = await session.execute(ips_query)
                ips = ips_result.scalars().first()

                if not ips:
                    raise NoAvailableIpsError()

                keys = Keys(WireguardKeys())
                session.add(keys)
                await session.flush()

                new_client = Client(
                    user_id=user_id,
                    device_num=devices_num + 1,
                    end_date=get_next_date(),
                    keys_id=keys.id,
                )
                session.add(new_client)
                await session.flush()

                ips.client_id = new_client.id

                await session.commit()
                return new_client

    async def get_clint_by_user_id_and_device_num(
        self, user_id: int, device_num: int
    ) -> Client:
        async with self.session_maker() as session:
            # noinspection PyTypeChecker
            query = select(Client).where(
                Client.user_id == user_id, Client.device_num == device_num
            )
            result = await session.execute(query)
            return result.scalars().first()

    async def delete_client(self, client: Client):
        ips = await self.get_ips_by_client_id(client.id)
        keys = await self.get_keys_by_client_id(client.id)
        async with self.session_maker() as session:
            async with session.begin():
                ips.client_id = None
                await session.delete(client)
                await session.delete(keys)
            await session.commit()


db_manager = DBManager()

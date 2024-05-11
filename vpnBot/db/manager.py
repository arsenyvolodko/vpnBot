import asyncio

from sqlalchemy import select, null
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine

from vpnBot import config
from vpnBot.db.tables import *
from vpnBot.enums.operation_type_enum import OperationTypeEnum

from vpnBot.exceptions.clients import *
from vpnBot.exceptions.promo_codes import *
from vpnBot.static.common import *
from vpnBot.utils.date_util import get_next_date
from vpnBot.wireguard_tools.wireguard_client import WireguardClient


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
        async with EngineManager(config.DATABASE_URL) as engine:
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

    async def add_client(self, user_id: int) -> Client:
        async with self.session_maker() as session:
            async with session.begin():
                # noinspection PyTypeChecker
                devices_query = select(Client).where(Client.user_id == user_id)
                devices_result = await session.execute(devices_query)
                devices = devices_result.scalars().all()

                if len(devices) == DEVICES_MAX_AMOUNT:
                    raise DevicesLimitError()

                new_device_num = devices[-1].device_num + 1 if devices else 1

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
                    device_num=new_device_num,
                    end_date=get_next_date(),
                    keys_id=keys.id,
                )
                session.add(new_client)
                await session.flush()
                ips.client_id = new_client.id

                wg_config = config.WIREGUARD_CONFIG_MAP[ips.interface]
                wg_client = WireguardClient(
                    name=f"{user_id}_{new_device_num}",
                    ipv4=ips.ipv4,
                    ipv6=ips.ipv6,
                    keys=keys.get_as_wg_keys(),
                    endpoint=wg_config.endpoint,
                )
                await wg_config.add_client(wg_client)

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

    async def _get_wg_client_by_client(self, client: Client):
        ips = await self.get_ips_by_client_id(client.id)
        wg_config = config.WIREGUARD_CONFIG_MAP[ips.interface]
        keys = await self.get_keys_by_client_id(client.id)
        wg_client = WireguardClient(
            name=f"{client.user_id}_{client.device_num}",
            ipv4=ips.ipv4,
            ipv6=ips.ipv6,
            keys=keys.get_as_wg_keys(),
            endpoint=wg_config.endpoint,
        )
        return wg_client

    async def delete_client(self, client: Client) -> None:
        ips = await self.get_ips_by_client_id(client.id)
        keys = await self.get_keys_by_client_id(client.id)
        async with self.session_maker() as session:
            async with session.begin():

                wg_config = config.WIREGUARD_CONFIG_MAP[ips.interface]
                wg_client = await self._get_wg_client_by_client(client)

                ips.client_id = None
                await session.delete(client)
                await session.delete(keys)

                await wg_config.remove_client(wg_client)
            await session.commit()

    async def get_user_transactions(self, user_id) -> list[Transaction]:
        async with self.session_maker() as session:
            async with session.begin():
                query = select(Transaction).where(Transaction.user_id == user_id)
                result = await session.execute(query)
                return result.scalars().all()

    async def add_promo_code_usage(
        self, promo_code_text: str, user_id: int
    ) -> PromoCode:
        async with self.session_maker() as session:
            async with session.begin():

                promo_code_query = select(PromoCode).where(
                    PromoCode.name == promo_code_text
                )
                promo_code_result = await session.execute(promo_code_query)
                promo_code: PromoCode = promo_code_result.scalars().first()

                if not promo_code:
                    raise NoSuchPromoCodeError()

                # noinspection PyTypeChecker
                used_promo_code_query = select(UsedPromoCode).where(
                    UsedPromoCode.promo_code_id == promo_code.id,
                    UsedPromoCode.user_id == user_id,
                )
                used_promo_code_result = await session.execute(used_promo_code_query)
                used_promo_code = used_promo_code_result.scalars().first()

                if used_promo_code:
                    raise AlreadyUsedPromoCodeError()

                if not promo_code.active:
                    raise PromoCodeInactiveError()

                new_promo_code_usage = UsedPromoCode(
                    user_id=user_id, promo_code_id=promo_code.id
                )

                session.add(new_promo_code_usage)

                await self.update_balance(
                    session,
                    user_id,
                    promo_code.value,
                    OperationTypeEnum.INCREASE,
                    comment=TransactionCommentEnum.PROMO_CODE,
                )

                await session.commit()
                return promo_code


db_manager = DBManager()

import asyncio

from sqlalchemy import select, null, update
from sqlalchemy.ext.asyncio import async_sessionmaker

from vpnBot import config
from vpnBot.db.engine_manager import EngineManager
from vpnBot.db.tables import *
from vpnBot.enums.operation_type_enum import OperationTypeEnum
from vpnBot.exceptions.clients import *
from vpnBot.exceptions.clients.no_such_client_error import NoSuchClientError
from vpnBot.exceptions.promo_codes import *
from vpnBot.consts.common import *
from vpnBot.utils.date_util import get_next_date
from wireguard_tools.wireguard_client import WireguardClient


class DBManager:
    def __init__(self):
        self.session_maker = None
        asyncio.run(self._init())

    async def _init(self):
        async with EngineManager(config.DATABASE_URL) as engine:
            self.session_maker = async_sessionmaker(engine, expire_on_commit=False)
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

    async def close(self):
        async with self.session_maker() as session:
            session.close()

    async def add_record(self, new_record) -> Base:
        async with self.session_maker() as session:
            async with session.begin():
                session.add(new_record)
                await session.commit()
                return new_record

    async def get_records(self, model: type[Base], **kwargs):
        query = select(model).where(
            *[getattr(model, key) == value for key, value in kwargs.items()]
        )
        async with self.session_maker() as session:
            result = await session.execute(query)
            records = result.scalars().all()
        return records

    async def get_record(self, model: type[Base], **kwargs):
        return (
            records[0]
            if (records := (await self.get_records(model, **kwargs)))
            else None
        )

    async def delete_record(self, record: Base):
        async with self.session_maker() as session:
            async with session.begin():
                session.delete(record)
                await session.commit()

    # noinspection PyTypeChecker
    async def get_keys_by_client_id(self, client_id: int) -> Keys | None:
        async with self.session_maker() as session:
            query = select(Keys).join(Client).where(Client.id == client_id)
            result = await session.execute(query)
            return result.scalars().first()

    @staticmethod
    async def _add_transaction_util(
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

    async def update_balance(self, **kwargs) -> bool:
        if kwargs.get("session", None):
            return await self._update_balance_util(**kwargs)

        async with self.session_maker() as session:
            async with session.begin():
                return await self._update_balance_util(session, **kwargs)

    @staticmethod
    async def _update_balance_util(
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
        await DBManager._add_transaction_util(
            session, user_id=user_id, value=value, op_type=op_type, comment=comment
        )
        return True

    async def add_client(self, user_id: int) -> Client:
        async with self.session_maker() as session:
            async with session.begin():
                # noinspection PyTypeChecker
                devices_query = select(Client).where(Client.user_id == user_id)
                devices_result = await session.execute(devices_query)
                devices = sorted(list(devices_result.scalars().all()))

                if len(devices) == DEVICES_MAX_AMOUNT:
                    raise DevicesLimitError()

                new_device_num = devices[-1].device_num + 1 if devices else 1

                balance_updated = await self.update_balance(
                    user_id=user_id,
                    value=PRICE,
                    op_type=OperationTypeEnum.DECREASE,
                    comment=TransactionCommentEnum.ADD_DEVICE,
                    session=session,
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
                    keys=keys.get_as_wg_keys(),
                    endpoint=wg_config.endpoint,
                    server_public_key=wg_config.public_key,
                )
                await wg_config.add_client(wg_client)
                await session.commit()
                return new_client

    async def _get_wg_client_by_client(self, client: Client):
        ips = await db_manager.get_record(Ips, client_id=client.id)
        wg_config = config.WIREGUARD_CONFIG_MAP[ips.interface]
        keys = await self.get_keys_by_client_id(client.id)
        wg_client = WireguardClient(
            name=f"{client.user_id}_{client.device_num}",
            ipv4=ips.ipv4,
            keys=keys.get_as_wg_keys(),
            endpoint=wg_config.endpoint,
            server_public_key=wg_config.public_key,
        )
        return wg_client

    async def delete_client(self, client: Client) -> None:
        ips = await db_manager.get_record(Ips, client_id=client.id)
        keys = await self.get_keys_by_client_id(client.id)
        if not keys or not ips:
            return
        async with self.session_maker() as session:
            async with session.begin():
                wg_config = config.WIREGUARD_CONFIG_MAP[ips.interface]
                wg_client = await self._get_wg_client_by_client(client)

                ips.client_id = None
                await session.delete(client)
                await session.delete(keys)

                await wg_config.remove_client(wg_client)
            await session.commit()

    async def add_promo_code_usage(
        self, promo_code_text: str, user_id: int
    ) -> PromoCode:
        async with self.session_maker() as session:
            async with session.begin():

                # noinspection PyTypeChecker
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
                    user_id=user_id,
                    value=promo_code.value,
                    op_type=OperationTypeEnum.INCREASE,
                    comment=TransactionCommentEnum.PROMO_CODE,
                    session=session,
                )

                await session.commit()
                return promo_code

    async def get_clients_by_end_date(
        self, end_date: datetime.date, activity_status: bool
    ) -> list[Client]:
        async with self.session_maker() as session:
            async with session.begin():
                # noinspection PyTypeChecker
                query = select(Client).where(
                    Client.end_date <= end_date, Client.active == activity_status
                )
                result = await session.execute(query)
                return result.scalars().all()

    async def renew_subscription(
        self, client_id: int, user_id: int, end_date: datetime.date
    ):
        client = await self.get_record(Client, id=client_id)
        wg_client = await self._get_wg_client_by_client(client)
        ips = await db_manager.get_record(Ips, client_id=client.id)
        wg_config = config.WIREGUARD_CONFIG_MAP[ips.interface]

        async with self.session_maker() as session:
            async with session.begin():
                updated = await self.update_balance(
                    user_id=user_id,
                    value=PRICE,
                    op_type=OperationTypeEnum.DECREASE,
                    comment=TransactionCommentEnum.RENEW_SUBSCRIPTION,
                    session=session,
                )
                if not updated:
                    # noinspection PyTypeChecker
                    query = (
                        update(Client)
                        .values(active=False)
                        .where(Client.id == client_id)
                    )
                    await wg_config.remove_client(wg_client)
                    await session.execute(query)
                    await session.commit()
                    raise NotEnoughMoneyError()
                # noinspection PyTypeChecker
                query = (
                    update(Client)
                    .values(end_date=end_date)
                    .where(Client.id == client_id)
                )
                await session.execute(query)
                await session.commit()

    async def resume_device_subscription(self, client_id: int, user_id: int):
        async with self.session_maker() as session:
            async with session.begin():
                client = await self.get_record(Client, id=client_id)
                ips = await db_manager.get_record(Ips, client_id=client.id)
                keys = await self.get_keys_by_client_id(client_id)
                if not client:
                    raise NoSuchClientError()

                balance_updated = await self.update_balance(
                    user_id=user_id,
                    value=PRICE,
                    op_type=OperationTypeEnum.DECREASE,
                    comment=TransactionCommentEnum.RENEW_SUBSCRIPTION,
                    session=session,
                )
                if not balance_updated:
                    raise NotEnoughMoneyError()

                # noinspection PyTypeChecker
                query = (
                    update(Client)
                    .values(active=True, end_date = get_next_date())
                    .where(Client.id == client_id)
                )
                await session.execute(query)

                wg_config = config.WIREGUARD_CONFIG_MAP[ips.interface]
                wg_client = WireguardClient(
                    name=f"{user_id}_{client.device_num}",
                    ipv4=ips.ipv4,
                    keys=keys.get_as_wg_keys(),
                    endpoint=wg_config.endpoint,
                    server_public_key=wg_config.public_key,
                )
                await wg_config.add_client(wg_client)
                await session.commit()

    async def update_payment_status(self, payment_id: int, status: PaymentStatusEnum):
        async with self.session_maker() as session:
            async with session.begin():
                payment: Payment = await self.get_record(Payment, id=payment_id)
                payment.status = status
                await session.commit()


db_manager = DBManager()

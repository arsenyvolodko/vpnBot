from datetime import datetime
from sqlalchemy import BigInteger, Column, ForeignKey, Date, DateTime, UniqueConstraint
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from vpnBot.enums import *
from vpnBot.consts.common import PRICE
from wireguard_tools.wireguard_keys import WireguardKeys


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=False,
    )

    username: Mapped[str] = mapped_column(unique=True, nullable=False)

    balance: Mapped[int] = mapped_column(nullable=False, default=PRICE)

    join_date = Column(Date, nullable=False, default=datetime.now().date())

    inviter_id = Column(BigInteger, ForeignKey('user.id'), nullable=True, default=None)


class Ips(Base):
    __tablename__ = "ips"

    id: Mapped[int] = mapped_column(primary_key=True)

    interface: Mapped[str] = mapped_column(nullable=False, default='wg0')

    ipv4: Mapped[str] = mapped_column(unique=True, nullable=False)

    ipv6: Mapped[str] = mapped_column(unique=True, nullable=False)

    client_id: Mapped[int] = mapped_column(
        ForeignKey("client.id"), nullable=True, default=None
    )

    client = relationship("Client", back_populates="ips")


class Keys(Base):
    __tablename__ = "keys"

    id: Mapped[int] = mapped_column(primary_key=True)

    public_key: Mapped[str] = mapped_column(unique=True, nullable=False)

    private_key: Mapped[str] = mapped_column(unique=True, nullable=False)

    client = relationship("Client", back_populates="keys", uselist=False)

    def __init__(self, keys: WireguardKeys):
        super().__init__(public_key=keys.public_key, private_key=keys.private_key)

    def get_as_wg_keys(self):
        return WireguardKeys(private_key=self.private_key, public_key=self.public_key)


class Client(Base):
    __tablename__ = "client"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False)

    device_num: Mapped[int] = mapped_column(nullable=False)

    active: Mapped[bool] = mapped_column(nullable=False, default=True)

    end_date = Column(Date, nullable=False)

    keys_id: Mapped[int] = mapped_column(
        ForeignKey("keys.id"), nullable=False, unique=True
    )

    user = relationship("User", backref="clients")
    keys = relationship("Keys", back_populates="client", uselist=False)
    ips = relationship("Ips", back_populates="client", uselist=False)

    __table_args__ = (
        UniqueConstraint('user_id', 'device_num'),
    )


class Transaction(Base):
    __tablename__ = "transaction"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False)

    value: Mapped[int] = mapped_column(nullable=False)

    operation_type: Mapped[OperationTypeEnum] = mapped_column(nullable=False)

    operation_time = Column(DateTime, nullable=False, default=datetime.now)

    comment: Mapped[TransactionCommentEnum] = mapped_column(nullable=False)


class PromoCode(Base):
    __tablename__ = "promo_code"

    id: Mapped[int] = mapped_column(primary_key=True)

    value: Mapped[int] = mapped_column(nullable=False)

    name: Mapped[str] = mapped_column(unique=True, nullable=False)

    active: Mapped[bool] = mapped_column(nullable=False, default=True)


class UsedPromoCode(Base):
    __tablename__ = "used_promo_code"

    user_id = Column(BigInteger, ForeignKey("user.id"), primary_key=True)

    promo_code_id: Mapped[int] = mapped_column(
        ForeignKey("promo_code.id"), primary_key=True
    )


class Payment(Base):
    __tablename__ = "payment"

    id: Mapped[str] = mapped_column(primary_key=True)

    user_id = Column(
        BigInteger,
        ForeignKey("user.id"),
    )

    status: Mapped[PaymentStatusEnum] = mapped_column(
        nullable=False, default=PaymentStatusEnum.PENDING
    )

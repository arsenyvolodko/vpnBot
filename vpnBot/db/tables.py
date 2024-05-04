import subprocess
from datetime import datetime
from sqlalchemy import BigInteger, Column, ForeignKey, Date, DateTime
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from vpnBot.enums.payment_status_enum import PaymentStatusEnum
from vpnBot.enums.transaction_comment_enum import TransactionCommentEnum
from vpnBot.static.common import PRICE


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=False,
    )

    username: Mapped[str] = mapped_column(
        unique=True,
        nullable=False
    )

    balance: Mapped[int] = mapped_column(
        nullable=False,
        default=PRICE
    )

    join_date = Column(
        Date,
        nullable=False,
        default=datetime.now().date()
    )


class Ips(Base):
    __tablename__ = "ips"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    interface: Mapped[int] = mapped_column(
        nullable=False,
        default=0
    )

    ipv4: Mapped[str] = mapped_column(
        unique=True,
        nullable=False
    )

    ipv6: Mapped[str] = mapped_column(
        unique=True,
        nullable=False
    )

    client_id: Mapped[int] = mapped_column(
        ForeignKey('client.id'),
        nullable=True,
        default=None
    )

    client = relationship("Client", back_populates="ips")


class Keys(Base):
    __tablename__ = "keys"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    public_key: Mapped[str] = mapped_column(
        unique=True,
        nullable=False
    )

    preshared_key: Mapped[str] = mapped_column(
        unique=True,
        nullable=False
    )

    private_key: Mapped[str] = mapped_column(
        unique=True,
        nullable=False
    )

    client = relationship("Client", back_populates="keys", uselist=False)

    @staticmethod
    def _generate_private_key() -> str:
        return subprocess.check_output(
            ["wg", "genkey"],
            text=True,
            stderr=subprocess.PIPE
        ).strip()

    @staticmethod
    def _generate_public_key(private_key: str) -> str:
        return subprocess.check_output(
            ["wg", "pubkey"],
            text=True,
            input=private_key,
            stderr=subprocess.PIPE).strip()

    @staticmethod
    def _generate_preshared_key() -> str:
        return subprocess.check_output(
            ["wg", "genpsk"],
            text=True,
            stderr=subprocess.PIPE
        ).strip()

    @staticmethod
    def generate_keys() -> 'Keys':
        private_key = Keys._generate_private_key()
        public_key = Keys._generate_public_key(private_key)
        preshared_key = Keys._generate_preshared_key()
        return Keys(
            public_key=public_key,
            preshared_key=preshared_key,
            private_key=private_key
        )


class Client(Base):
    __tablename__ = "client"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    user_id = Column(
        BigInteger,
        ForeignKey("user.id"),
        nullable=False
    )

    device_num: Mapped[int] = mapped_column(
        nullable=False
    )

    active: Mapped[bool] = mapped_column(
        nullable=False,
        default=1
    )

    end_date = Column(
        Date,
        nullable=False
    )

    keys_id: Mapped[int] = mapped_column(
        ForeignKey("keys.id"),
        nullable=False,
        unique=True
    )

    user = relationship("User", backref="clients")
    keys = relationship("Keys", back_populates="client", uselist=False)
    # keys = relationship("Keys", back_populates="client", foreign_keys=[keys_id], uselist=False)
    ips = relationship("Ips", back_populates='client', uselist=False)


class Transaction(Base):
    __tablename__ = 'transaction'

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    user_id = Column(
        BigInteger,
        ForeignKey("user.id"),
        nullable=False
    )

    operation_type: Mapped[bool] = mapped_column(
        nullable=False
    )

    operation_time = Column(
        DateTime,
        nullable=False,
        default=datetime.now
    )

    comment: Mapped[TransactionCommentEnum] = mapped_column(
        nullable=False
    )


class PromoCode(Base):
    __tablename__ = 'promo_code'

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    value: Mapped[int] = mapped_column(
        nullable=False
    )

    name: Mapped[str] = mapped_column(
        unique=True,
        nullable=False
    )


class UsedPromoCode(Base):
    __tablename__ = 'used_promo_code'

    user_id = Column(
        BigInteger,
        ForeignKey('user.id'),
        primary_key=True
    )

    promo_code_id: Mapped[int] = mapped_column(
        ForeignKey('promo_code.id'),
        primary_key=True
    )


class Payment(Base):
    __tablename__ = 'payment'

    id: Mapped[str] = mapped_column(
        primary_key=True
    )

    user_id = Column(
        BigInteger,
        ForeignKey('user.id'),
    )

    status: Mapped[PaymentStatusEnum] = mapped_column(
        nullable=False,
        default=PaymentStatusEnum.PENDING
    )

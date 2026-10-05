import functools
from datetime import datetime
from typing import Optional

from sqlalchemy import Engine, ForeignKey, MetaData
from cyberfusion.RabbitMQConsumerLogServer.settings import settings
from sqlalchemy import create_engine, Integer, String
from sqlalchemy.dialects.mysql import DATETIME, LONGTEXT
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase, mapped_column, Mapped


@functools.cache
def get_engine() -> Engine:
    return create_engine(settings.database_uri, pool_pre_ping=True)


def make_database_session() -> Session:
    return sessionmaker(bind=get_engine())()


naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata_obj = MetaData(naming_convention=naming_convention)


class Base(DeclarativeBase):
    metadata = metadata_obj


class BaseModel(Base):
    """Base model."""

    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DATETIME(fsp=6), default=datetime.utcnow
    )


class RPCRequestLog(BaseModel):
    """RPC request log model."""

    __tablename__ = "rpc_requests_logs"

    correlation_id: Mapped[str] = mapped_column(String(length=36), unique=True)
    request_payload: Mapped[str] = mapped_column(LONGTEXT)
    virtual_host_name: Mapped[str] = mapped_column(String(length=255))
    exchange_name: Mapped[str] = mapped_column(String(length=255))
    queue_name: Mapped[str] = mapped_column(String(length=255))
    hostname: Mapped[str] = mapped_column(String(length=255))
    rabbitmq_username: Mapped[str] = mapped_column(String(length=255))


class RPCResponseLog(BaseModel):
    """RPC response log model."""

    __tablename__ = "rpc_responses_logs"

    correlation_id: Mapped[str] = mapped_column(
        String(length=36),
        ForeignKey("rpc_requests_logs.correlation_id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    response_payload: Mapped[str] = mapped_column(LONGTEXT)
    traceback: Mapped[Optional[str]] = mapped_column(LONGTEXT)

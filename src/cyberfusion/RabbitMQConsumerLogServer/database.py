from datetime import datetime

from sqlalchemy import ForeignKey
from cyberfusion.RabbitMQConsumerLogServer.settings import settings
from sqlalchemy import create_engine, Column, DateTime, Integer, JSON, String
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


def make_database_session() -> Session:
    engine = create_engine(
        "sqlite:///" + settings.database_path, connect_args={"check_same_thread": False}
    )

    return sessionmaker(bind=engine)()


Base = declarative_base()


class BaseModel(Base):  # type: ignore[misc, valid-type]
    """Base model."""

    __abstract__ = True

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class RPCRequestLog(BaseModel):
    """RPC request log model."""

    __tablename__ = "rpc_requests_logs"

    correlation_id = Column(String(length=36), unique=True, nullable=False)
    request_payload = Column(JSON, nullable=False)
    virtual_host_name = Column(String(length=255), nullable=False)
    exchange_name = Column(String(length=255), nullable=False)
    queue_name = Column(String(length=255), nullable=False)
    hostname = Column(String(length=255), nullable=False)
    rabbitmq_username = Column(String(length=255), nullable=False)


class RPCResponseLog(BaseModel):
    """RPC response log model."""

    __tablename__ = "rpc_responses_logs"

    correlation_id = Column(
        String(length=36),
        ForeignKey("rpc_requests_logs.correlation_id"),
        unique=True,
        nullable=False,
    )
    response_payload = Column(JSON, nullable=False)
    traceback = Column(JSON, nullable=True)

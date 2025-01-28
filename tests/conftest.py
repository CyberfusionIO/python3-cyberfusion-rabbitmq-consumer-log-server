import os
from typing import List, Generator
from alembic import command
from alembic.config import Config
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from cyberfusion.RabbitMQConsumerLogServer.database import RPCRequestLog
from cyberfusion.RabbitMQConsumerLogServer.fastapi import app
import pytest

from cyberfusion.RabbitMQConsumerLogServer import database
from cyberfusion.RabbitMQConsumerLogServer.seeders import (
    seed_rpc_request_logs,
    seed_rpc_response_logs,
)
from cyberfusion.RabbitMQConsumerLogServer.settings import settings


@pytest.fixture
def test_client() -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def sqlite_database() -> Generator[None, None, None]:
    database_path = os.path.join(os.path.sep, "tmp", str(os.getpid()))

    settings.database_path = database_path

    alembic_config = Config(file_="alembic.local.ini")
    alembic_config.set_main_option("sqlalchemy.url", "sqlite:///" + database_path)

    command.upgrade(alembic_config, "head")

    yield

    os.remove(database_path)


@pytest.fixture
def database_session() -> Session:
    return database.make_database_session()


@pytest.fixture
def rpc_request_logs(database_session: Session) -> List[database.RPCRequestLog]:
    return seed_rpc_request_logs(database_session)


@pytest.fixture
def rpc_response_logs(
    database_session: Session, rpc_request_logs: List[RPCRequestLog]
) -> List[database.RPCResponseLog]:
    return seed_rpc_response_logs(database_session, rpc_request_logs)

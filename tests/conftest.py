from typing import List, Generator
from alembic import command
from alembic.config import Config
from pytest_mock import MockerFixture
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session
from sqlalchemy_utils import create_database, database_exists, drop_database
from fastapi.testclient import TestClient
from _pytest.config.argparsing import Parser

from cyberfusion.RabbitMQConsumerLogServer.database import RPCRequestLog
from cyberfusion.RabbitMQConsumerLogServer.fastapi import app
import pytest

from cyberfusion.RabbitMQConsumerLogServer import database
from cyberfusion.RabbitMQConsumerLogServer.seeders import (
    seed_rpc_request_logs,
    seed_rpc_response_logs,
)
from cyberfusion.RabbitMQConsumerLogServer.settings import settings


@pytest.fixture(scope="session", autouse=True)
def database_session(
    worker_id: str, option_mariadb_admin_uri: str, session_mocker: MockerFixture
) -> Generator[Session, None, None]:
    # Create worker-specific database for parallelisation

    url = (
        make_url(option_mariadb_admin_uri)
        .set(database=f"rcls_{worker_id}")
        .render_as_string(hide_password=False)
    )

    # Set database URI for app

    settings.database_uri = url

    # Drop database if it wasn't cleaned up during a previous test run

    if database_exists(url):
        drop_database(url)

    # Create database

    create_database(url)

    # Create database session

    database_session = database.make_database_session()

    try:
        # Run Alembic migrations

        alembic_config = Config(file_="alembic.local.ini")
        alembic_config.set_main_option("sqlalchemy.url", url)

        command.upgrade(alembic_config, "head")

        # Use this database session. Using the same session for tests and in-app
        # means changes on either side is reflected on both sides. Without it,
        # MariaDB's default transaction isolation level hides changes committed
        # by the other side.

        session_mocker.patch.object(
            database, "make_database_session", return_value=database_session
        )

        # Return database session

        yield database_session
    finally:
        database_session.close()

        drop_database(url)


@pytest.fixture(autouse=True)
def clean_database(database_session: Session) -> Generator[None, None, None]:
    yield

    database_session.rollback()

    # Clear every table in the database. Foreign key checks are disabled, so the
    # delete order does not matter.

    table_names = [
        table_name
        for (table_name,) in database_session.execute(text("SHOW TABLES"))
        if table_name != "alembic_version"
    ]

    database_session.execute(text("SET FOREIGN_KEY_CHECKS = 0"))

    for table_name in table_names:
        database_session.execute(text(f"DELETE FROM `{table_name}`"))

    database_session.execute(text("SET FOREIGN_KEY_CHECKS = 1"))

    database_session.commit()


@pytest.fixture
def test_client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def rpc_request_logs(database_session: Session) -> List[database.RPCRequestLog]:
    return seed_rpc_request_logs(database_session)


@pytest.fixture
def rpc_response_logs(
    database_session: Session, rpc_request_logs: List[RPCRequestLog]
) -> List[database.RPCResponseLog]:
    return seed_rpc_response_logs(database_session, rpc_request_logs)


@pytest.fixture(scope="session")
def option_mariadb_admin_uri(request: pytest.FixtureRequest) -> str:
    return request.config.getoption("--mariadb-admin-uri")


def pytest_addoption(parser: Parser) -> None:
    parser.addoption(
        "--mariadb-admin-uri",
        action="store",
        type=str,
        required=True,
        help="User must have permission to create and drop databases",
    )

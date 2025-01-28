from faker import Faker
import os
import random
from typing import List
import uuid
from alembic import command
from alembic.config import Config
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from cyberfusion.RabbitMQConsumerLogServer.database import RPCRequestLog
from cyberfusion.RabbitMQConsumerLogServer.fastapi import app
import pytest

from cyberfusion.RabbitMQConsumerLogServer import database
from cyberfusion.RabbitMQConsumerLogServer.settings import settings

faker = Faker()


tracebacks = [
    """Traceback (most recent call last):
  File "/opt/api/lib/python3.11/site-packages/starlette/middleware/base.py", line 159, in call_next
    message = await recv_stream.receive()
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/api/lib/python3.11/site-packages/anyio/streams/memory.py", line 118, in receive
    raise EndOfStream
anyio.EndOfStream
During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/opt/api/lib/python3.11/site-packages/uvicorn/protocols/http/httptools_impl.py", line 401, in run_asgi
    result = await app(  # type: ignore[func-returns-value]
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/api/lib/python3.11/site-packages/uvicorn/middleware/proxy_headers.py", line 70, in __call__
    return await self.app(scope, receive, send)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/api/lib/python3.11/site-packages/fastapi/applications.py", line 1054, in __call__
    await super().__call__(scope, receive, send)
  File "/opt/api/lib/python3.11/site-packages/starlette/applications.py", line 123, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/opt/api/lib/python3.11/site-packages/starlette/middleware/errors.py", line 186, in __call__
    raise exc
  File "/opt/api/lib/python3.11/site-packages/starlette/middleware/errors.py", line 164, in __call__
    await self.app(scope, receive, _send)
  File "/opt/api/lib/python3.11/site-packages/starlette/middleware/base.py", line 191, in __call__
    response = await self.dispatch_func(request, call_next)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/api/app/main.py", line 763, in database_session_middleware
    response = await call_next(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^""",
    """Traceback (most recent call last):
  File "/opt/api/lib/python3.11/site-packages/fastapi/routing.py", line 269, in app
    solved_result = await solve_dependencies(
                    ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/api/lib/python3.11/site-packages/fastapi/dependencies/utils.py", line 600, in solve_dependencies
    solved = await call(**sub_values)
             ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/api/app/api/dependencies.py", line 201, in get_common_parameters
    key, value = f.split(":", 1)
    ^^^^^^^^^^
ValueError: not enough values to unpack (expected 2, got 1)""",
    """Traceback (most recent call last):
  File "<stdin>", line 2, in <module>
Exception: An error""",
]


@pytest.fixture
def test_client() -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def sqlite_database() -> None:
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
    result = []

    for _ in range(1, 50):
        rpc_request_log = database.RPCRequestLog(
            correlation_id=str(uuid.uuid4()),
            request_payload=faker.json(),
            virtual_host_name=faker.word(),
            hostname=faker.hostname(),
            rabbitmq_username=faker.user_name(),
            queue_name=faker.word(),
            exchange_name=faker.word(),
        )

        database_session.add(rpc_request_log)

        result.append(rpc_request_log)

    database_session.commit()

    result.reverse()  # Newest first

    return result


@pytest.fixture
def rpc_response_logs(
    database_session: Session, rpc_request_logs: List[RPCRequestLog]
) -> List[database.RPCResponseLog]:
    result = []

    for rpc_request_log in rpc_request_logs:
        rpc_response_log = database.RPCResponseLog(
            correlation_id=rpc_request_log.correlation_id,
            response_payload=faker.json(),
            traceback=random.choice(tracebacks + [None]),
        )

        database_session.add(rpc_response_log)

        result.append(rpc_response_log)

    database_session.commit()

    result.reverse()  # Newest first

    return result

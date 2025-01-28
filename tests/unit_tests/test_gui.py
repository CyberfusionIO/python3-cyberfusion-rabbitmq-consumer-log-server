from cyberfusion.RabbitMQConsumerLogServer.database import RPCResponseLog
from cyberfusion.RabbitMQConsumerLogServer.settings import settings
from fastapi.testclient import TestClient
import uuid
from typing import List
from cyberfusion.RabbitMQConsumerLogServer import database
from sqlalchemy.orm import Session


def test_get_rpc_request_detail_without_traceback(
    database_session: Session,
    test_client: TestClient,
    rpc_request_logs: List[database.RPCRequestLog],
    rpc_response_logs: list[database.RPCResponseLog],
) -> None:
    rpc_response_log = [x for x in rpc_response_logs if x.traceback is None][0]

    response = test_client.get(
        "/rpc-requests/" + rpc_response_log.correlation_id,
        auth=("ignored", settings.gui_password),
    )

    assert response.status_code == 200
    assert "Traceback" not in response.text


def test_get_rpc_request_detail_with_traceback(
    database_session: Session,
    test_client: TestClient,
    rpc_request_logs: List[database.RPCRequestLog],
    rpc_response_logs: list[database.RPCResponseLog],
) -> None:
    rpc_response_log = [x for x in rpc_response_logs if x.traceback is not None][0]

    response = test_client.get(
        "/rpc-requests/" + rpc_response_log.correlation_id,
        auth=("ignored", settings.gui_password),
    )

    assert response.status_code == 200
    assert "Traceback" in response.text


def test_get_rpc_request_detail_without_rpc_response(
    database_session: Session,
    test_client: TestClient,
    rpc_request_logs: List[database.RPCRequestLog],
) -> None:
    assert database_session.query(RPCResponseLog).count() == 0

    response = test_client.get(
        "/rpc-requests/" + rpc_request_logs[0].correlation_id,
        auth=("ignored", settings.gui_password),
    )

    assert response.status_code == 200
    assert rpc_request_logs[0].correlation_id in response.text
    assert "No RPC response yet" in response.text


def test_get_rpc_request_detail_with_rpc_response(
    test_client: TestClient,
    rpc_request_logs: List[database.RPCRequestLog],
    rpc_response_logs: List[database.RPCResponseLog],
) -> None:
    response = test_client.get(
        "/rpc-requests/" + rpc_request_logs[0].correlation_id,
        auth=("ignored", settings.gui_password),
    )

    assert response.status_code == 200
    assert rpc_request_logs[0].correlation_id in response.text
    assert "No RPC response yet" not in response.text


def test_get_rpc_requests_overview_invalid_credentials(
    test_client: TestClient,
) -> None:
    response = test_client.get(
        "/rpc-requests",
        auth=("ignored", "invalid"),
    )

    assert response.status_code == 401


def test_get_rpc_request_detail_invalid_credentials(
    test_client: TestClient,
    rpc_request_logs: List[database.RPCRequestLog],
) -> None:
    response = test_client.get(
        "/rpc-requests/" + rpc_request_logs[0].correlation_id,
        auth=("ignored", "invalid"),
    )

    assert response.status_code == 401


def test_get_rpc_request_detail_not_exists(
    test_client: TestClient,
    rpc_request_logs: List[database.RPCRequestLog],
    rpc_response_logs: List[database.RPCResponseLog],
) -> None:
    response = test_client.get(
        "/rpc-requests/" + str(uuid.uuid4()),
        auth=("ignored", settings.gui_password),
    )

    assert response.status_code == 404

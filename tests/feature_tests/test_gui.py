from cyberfusion.RabbitMQConsumerLogServer.settings import settings
from fastapi.testclient import TestClient

from typing import List
from cyberfusion.RabbitMQConsumerLogServer import database


def test_get_rpc_requests_overview(
    test_client: TestClient, rpc_request_logs: List[database.RPCRequestLog]
) -> None:
    response = test_client.get(
        "/rpc-requests",
        auth=("ignored", settings.gui_password),
    )

    assert response.status_code == 200
    assert rpc_request_logs[0].correlation_id in response.text


def test_get_rpc_requests_overview_limit(
    test_client: TestClient, rpc_request_logs: List[database.RPCRequestLog]
) -> None:
    response = test_client.get(
        "/rpc-requests",
        params={"limit": 1},
        auth=("ignored", settings.gui_password),
    )

    assert response.status_code == 200
    assert rpc_request_logs[0].correlation_id in response.text
    assert rpc_request_logs[1].correlation_id not in response.text


def test_get_rpc_requests_overview_offset(
    test_client: TestClient, rpc_request_logs: List[database.RPCRequestLog]
) -> None:
    response = test_client.get(
        "/rpc-requests",
        params={"offset": 1},
        auth=("ignored", settings.gui_password),
    )

    assert response.status_code == 200
    assert rpc_request_logs[0].correlation_id not in response.text
    assert rpc_request_logs[1].correlation_id in response.text


def test_get_rpc_request_detail(
    test_client: TestClient, rpc_request_logs: List[database.RPCRequestLog]
) -> None:
    response = test_client.get(
        "/rpc-requests/" + rpc_request_logs[0].correlation_id,
        auth=("ignored", settings.gui_password),
    )

    assert response.status_code == 200
    assert rpc_request_logs[0].correlation_id in response.text

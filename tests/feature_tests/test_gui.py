from cyberfusion.RabbitMQConsumerLogServer.gui import DEFAULT_LIMIT
from cyberfusion.RabbitMQConsumerLogServer.settings import settings
from fastapi.testclient import TestClient

from typing import List
from cyberfusion.RabbitMQConsumerLogServer import database


def test_get_rpc_requests_overview(
    test_client: TestClient,
    rpc_request_logs: List[database.RPCRequestLog],
    rpc_response_logs: List[database.RPCResponseLog],
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
    correlation_ids = [
        rpc_request_log.correlation_id for rpc_request_log in rpc_request_logs
    ]

    response = test_client.get(
        "/rpc-requests",
        params={"limit": 1},
        auth=("ignored", settings.gui_password),
    )

    assert response.status_code == 200
    assert correlation_ids[0] in response.text

    for correlation_id in correlation_ids[1:]:
        assert correlation_id not in response.text


def test_get_rpc_requests_overview_offset(
    test_client: TestClient, rpc_request_logs: List[database.RPCRequestLog]
) -> None:
    correlation_ids = [
        rpc_request_log.correlation_id for rpc_request_log in rpc_request_logs
    ]

    response = test_client.get(
        "/rpc-requests",
        params={"offset": 1},
        auth=("ignored", settings.gui_password),
    )

    assert response.status_code == 200
    assert correlation_ids[0] not in response.text

    for correlation_id in correlation_ids[1:][:DEFAULT_LIMIT]:
        assert correlation_id in response.text


def test_get_rpc_requests_overview_limit_offset(
    test_client: TestClient, rpc_request_logs: List[database.RPCRequestLog]
) -> None:
    correlation_ids = [
        rpc_request_log.correlation_id for rpc_request_log in rpc_request_logs
    ]

    response = test_client.get(
        "/rpc-requests",
        params={"offset": 1, "limit": 1},
        auth=("ignored", settings.gui_password),
    )

    assert response.status_code == 200
    assert correlation_ids[1] in response.text

    del correlation_ids[1]

    for correlation_id in correlation_ids:
        assert correlation_id not in response.text


def test_get_rpc_request_detail(
    test_client: TestClient, rpc_request_logs: List[database.RPCRequestLog]
) -> None:
    response = test_client.get(
        "/rpc-requests/" + rpc_request_logs[0].correlation_id,
        auth=("ignored", settings.gui_password),
    )

    assert response.status_code == 200
    assert rpc_request_logs[0].correlation_id in response.text

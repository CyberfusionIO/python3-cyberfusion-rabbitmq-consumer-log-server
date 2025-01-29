from fastapi.testclient import TestClient
from sqlalchemy.orm.session import Session

from cyberfusion.RabbitMQConsumerLogServer.seeders import generate_fake_rpc_response
from cyberfusion.RabbitMQConsumerLogServer.settings import settings
import uuid


def test_create_rpc_request_invalid_api_token(
    test_client: TestClient, database_session: Session
) -> None:
    response = test_client.post(
        "/api/v1/rpc-requests",
        headers={"X-API-Token": "invalid"},
    )

    assert response.json() == {"detail": "Invalid API token"}
    assert response.status_code == 401


def test_create_rpc_response_invalid_api_token(
    test_client: TestClient, database_session: Session
) -> None:
    response = test_client.post(
        "/api/v1/rpc-responses",
        headers={"X-API-Token": "invalid"},
    )

    assert response.json() == {"detail": "Invalid API token"}
    assert response.status_code == 401


def test_create_rpc_response_missing_rpc_request(
    test_client: TestClient, database_session: Session
) -> None:
    correlation_id = str(uuid.uuid4())

    response = test_client.post(
        "/api/v1/rpc-responses",
        headers={"X-API-Token": settings.api_token},
        json={
            "correlation_id": correlation_id,
            "response_payload": generate_fake_rpc_response(),
            "traceback": None,
        },
    )

    assert response.json() == {
        "detail": f"No RPC response with correlation ID {correlation_id}"
    }
    assert response.status_code == 400

from fastapi.testclient import TestClient
import json
from sqlalchemy.orm.session import Session
from cyberfusion.RabbitMQConsumerLogServer.database import RPCResponseLog, RPCRequestLog
from cyberfusion.RabbitMQConsumerLogServer.seeders import (
    generate_fake_rpc_request,
    generate_fake_rpc_response,
)
from cyberfusion.RabbitMQConsumerLogServer.settings import settings
import uuid
from faker import Faker
from typing import List

faker = Faker()


def test_create_rpc_request(test_client: TestClient, database_session: Session) -> None:
    correlation_id = str(uuid.uuid4())
    request_payload = generate_fake_rpc_request()
    virtual_host_name = faker.word()
    queue_name = faker.word()
    exchange_name = faker.word()
    hostname = faker.hostname()
    rabbitmq_username = faker.user_name()

    response = test_client.post(
        "/api/v1/rpc-requests",
        headers={"X-API-Token": settings.api_token},
        json={
            "correlation_id": correlation_id,
            "request_payload": request_payload,
            "virtual_host_name": virtual_host_name,
            "hostname": hostname,
            "rabbitmq_username": rabbitmq_username,
            "queue_name": queue_name,
            "exchange_name": exchange_name,
        },
    )

    assert response.json() == {"detail": "Object created"}
    assert response.status_code == 201

    assert database_session.query(RPCRequestLog).count() == 1

    rpc_request_log = database_session.query(RPCRequestLog).first()

    assert rpc_request_log.correlation_id == correlation_id
    assert json.loads(rpc_request_log.request_payload) == request_payload
    assert rpc_request_log.virtual_host_name == virtual_host_name
    assert rpc_request_log.queue_name == queue_name
    assert rpc_request_log.exchange_name == exchange_name
    assert rpc_request_log.hostname == hostname
    assert rpc_request_log.rabbitmq_username == rabbitmq_username
    assert rpc_request_log.created_at


def test_create_rpc_response(
    test_client: TestClient,
    database_session: Session,
    rpc_request_logs: List[RPCRequestLog],
) -> None:
    correlation_id = rpc_request_logs[0].correlation_id
    response_payload = generate_fake_rpc_response()
    traceback = 'Traceback (most recent call last):\n  File "<stdin>", line 2, in <module>\nException: An error\n'

    response = test_client.post(
        "/api/v1/rpc-responses",
        headers={"X-API-Token": settings.api_token},
        json={
            "correlation_id": correlation_id,
            "response_payload": response_payload,
            "traceback": traceback,
        },
    )

    assert response.json() == {"detail": "Object created"}
    assert response.status_code == 201

    rpc_response_log = database_session.query(RPCResponseLog).first()

    assert rpc_response_log.correlation_id == correlation_id
    assert json.loads(rpc_response_log.response_payload) == response_payload
    assert rpc_response_log.traceback == traceback
    assert rpc_response_log.created_at

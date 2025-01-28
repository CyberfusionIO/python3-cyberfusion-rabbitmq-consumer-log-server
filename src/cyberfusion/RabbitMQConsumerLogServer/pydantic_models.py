from typing import Any, Optional
from pydantic import BaseModel, UUID4
from pydantic import Json


class APIDetailMessage(BaseModel):
    detail: str


class RPCRequestLog(BaseModel):
    correlation_id: UUID4
    request_payload: Json[Any]
    virtual_host_name: str
    queue_name: str
    exchange_name: str
    hostname: str
    rabbitmq_username: str


class RPCResponseLog(BaseModel):
    correlation_id: UUID4
    response_payload: Json[Any]
    traceback: Optional[str]

from typing import Optional
from pydantic import BaseModel, UUID4


class APIDetailMessage(BaseModel):
    detail: str


class RPCRequestLog(BaseModel):
    correlation_id: UUID4
    request_payload: dict | list
    virtual_host_name: str
    queue_name: str
    exchange_name: str
    hostname: str
    rabbitmq_username: str


class RPCResponseLog(BaseModel):
    correlation_id: UUID4
    response_payload: dict
    traceback: Optional[str]

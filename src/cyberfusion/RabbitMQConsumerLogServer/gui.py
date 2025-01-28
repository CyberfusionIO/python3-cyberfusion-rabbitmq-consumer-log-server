import json
from fastapi import Query
from typing import Any
from fastapi import Depends, HTTPException
from pydantic import UUID4
from sqlalchemy.orm import Session
from starlette import status
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from cyberfusion.RabbitMQConsumerLogServer import database
from cyberfusion.RabbitMQConsumerLogServer.dependencies import (
    validate_credentials,
    get_database_session,
)
from fastapi import APIRouter

from cyberfusion.RabbitMQConsumerLogServer.settings import settings

router = APIRouter(dependencies=[Depends(validate_credentials)])

templates = Jinja2Templates(directory=settings.templates_directory)


@router.get(  # type: ignore[misc]
    "/rpc-requests",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
    summary="Get all RPC requests",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Incorrect GUI password",
        },
    },
)
def rpc_requests_overview(
    request: Request,
    database_session: Session = Depends(get_database_session),
    limit: int = Query(default=20, ge=1, le=20),
    offset: int = Query(
        default=0,
    ),
) -> Any:
    rpc_requests = (
        database_session.query(database.RPCRequestLog)
        .order_by(database.RPCRequestLog.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )

    rpc_responses = (
        database_session.query(database.RPCResponseLog)
        .filter(
            database.RPCResponseLog.correlation_id.in_(
                [x.correlation_id for x in rpc_requests]
            )
        )
        .all()
    )

    for rpc_request in rpc_requests:
        rpc_request.request_payload = json.loads(rpc_request.request_payload)

    # Get template

    return templates.TemplateResponse(
        name="rpc_requests_overview.html",
        context={
            "request": request,
            "rpc_requests": rpc_requests,
            "rpc_responses": {
                rpc_response.correlation_id: rpc_response
                for rpc_response in rpc_responses
            },
            "total_rpc_requests": database_session.query(
                database.RPCRequestLog
            ).count(),
            "offset": offset,
            "limit": limit,
        },
    )


@router.get(  # type: ignore[misc]
    "/rpc-requests/{correlation_id}",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
    summary="Get single RPC request",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Incorrect GUI password",
        },
        status.HTTP_404_NOT_FOUND: {"description": "RPC request doesn't exist"},
    },
)
def rpc_request_detail(
    request: Request,
    correlation_id: UUID4,
    database_session: Session = Depends(get_database_session),
) -> Any:
    rpc_request = (
        database_session.query(database.RPCRequestLog)
        .filter(database.RPCRequestLog.correlation_id == str(correlation_id))
        .first()
    )

    if not rpc_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    rpc_response = (
        database_session.query(database.RPCResponseLog)
        .filter(database.RPCResponseLog.correlation_id == str(correlation_id))
        .first()
    )

    rpc_request.request_payload = json.loads(rpc_request.request_payload)

    if rpc_response:
        rpc_response.response_payload = json.loads(rpc_response.response_payload)

    return templates.TemplateResponse(
        name="rpc_request_detail.html",
        context={
            "request": request,
            "rpc_request": rpc_request,
            "rpc_response": rpc_response,
        },
    )

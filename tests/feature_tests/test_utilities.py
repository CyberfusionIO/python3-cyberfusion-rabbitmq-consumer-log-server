from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from cyberfusion.RabbitMQConsumerLogServer import database
from cyberfusion.RabbitMQConsumerLogServer.settings import settings
from cyberfusion.RabbitMQConsumerLogServer.utilities import purge_logs


def test_purge_logs(
    database_session: Session,
    rpc_response_logs: list[database.RPCResponseLog],
    rpc_request_logs: list[database.RPCRequestLog],
) -> None:
    original_rpc_request_log_count = database_session.query(
        database.RPCRequestLog
    ).count()
    original_rpc_response_log_count = database_session.query(
        database.RPCResponseLog
    ).count()

    # Get RPC request log

    rpc_request_log = database_session.query(database.RPCRequestLog).first()

    # Check that an RPC response log exists belonging to the RPC request (will
    # be cascade-deleted)

    assert (
        database_session.query(database.RPCResponseLog)
        .filter(
            database.RPCResponseLog.correlation_id == rpc_request_log.correlation_id
        )
        .first()
    )

    # Pretend the RPC request is due to be purged

    rpc_request_log.created_at = datetime.utcnow() - timedelta(days=settings.keep_days)

    database_session.add(rpc_request_log)
    database_session.commit()
    database_session.refresh(rpc_request_log)

    # Execute purge

    purge_logs()

    # Check that the RPC request log has been deleted, and the corresponding RPC
    # response log has been cascade-deleted

    new_rpc_request_log_count = database_session.query(database.RPCRequestLog).count()
    new_rpc_response_log_count = database_session.query(database.RPCResponseLog).count()

    assert new_rpc_request_log_count == original_rpc_request_log_count - 1
    assert new_rpc_response_log_count == original_rpc_response_log_count - 1

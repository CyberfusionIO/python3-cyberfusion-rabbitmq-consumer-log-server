"""Initial migration

Revision ID: 7a5a16c86789
Revises:
Create Date: 2026-10-04 10:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import DATETIME, LONGTEXT


# revision identifiers, used by Alembic.
revision = "7a5a16c86789"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "rpc_requests_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", DATETIME(fsp=6), nullable=False),
        sa.Column("correlation_id", sa.String(length=36), nullable=False),
        sa.Column("request_payload", LONGTEXT(), nullable=False),
        sa.Column("virtual_host_name", sa.String(length=255), nullable=False),
        sa.Column("exchange_name", sa.String(length=255), nullable=False),
        sa.Column("queue_name", sa.String(length=255), nullable=False),
        sa.Column("hostname", sa.String(length=255), nullable=False),
        sa.Column("rabbitmq_username", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_rpc_requests_logs")),
        sa.UniqueConstraint(
            "correlation_id", name=op.f("uq_rpc_requests_logs_correlation_id")
        ),
    )
    op.create_table(
        "rpc_responses_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", DATETIME(fsp=6), nullable=False),
        sa.Column("correlation_id", sa.String(length=36), nullable=False),
        sa.Column("response_payload", LONGTEXT(), nullable=False),
        sa.Column("traceback", LONGTEXT(), nullable=True),
        sa.ForeignKeyConstraint(
            ["correlation_id"],
            ["rpc_requests_logs.correlation_id"],
            name=op.f("fk_rpc_responses_logs_correlation_id_rpc_requests_logs"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_rpc_responses_logs")),
        sa.UniqueConstraint(
            "correlation_id", name=op.f("uq_rpc_responses_logs_correlation_id")
        ),
    )


def downgrade() -> None:
    op.drop_table("rpc_responses_logs")
    op.drop_table("rpc_requests_logs")

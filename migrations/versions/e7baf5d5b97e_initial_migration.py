"""Initial migration

Revision ID: e7baf5d5b97e
Revises:
Create Date: 2025-01-28 20:06:26.237255

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e7baf5d5b97e"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "rpc_requests_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("correlation_id", sa.String(length=36), nullable=False),
        sa.Column("request_payload", sa.JSON(), nullable=False),
        sa.Column("virtual_host_name", sa.String(length=255), nullable=False),
        sa.Column("exchange_name", sa.String(length=255), nullable=False),
        sa.Column("queue_name", sa.String(length=255), nullable=False),
        sa.Column("hostname", sa.String(length=255), nullable=False),
        sa.Column("rabbitmq_username", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("correlation_id"),
    )
    op.create_table(
        "rpc_responses_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("correlation_id", sa.String(length=36), nullable=False),
        sa.Column("response_payload", sa.JSON(), nullable=False),
        sa.Column("traceback", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(
            ["correlation_id"],
            ["rpc_requests_logs.correlation_id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("correlation_id"),
    )


def downgrade() -> None:
    op.drop_table("rpc_responses_logs")
    op.drop_table("rpc_requests_logs")

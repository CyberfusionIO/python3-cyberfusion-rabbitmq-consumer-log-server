"""Initial migration

Revision ID: 12b6fe83f584
Revises:
Create Date: 2025-01-28 19:08:07.177404

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "12b6fe83f584"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "rpc_requests_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("correlation_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
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
        sa.Column("correlation_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("response_payload", sa.JSON(), nullable=False),
        sa.Column("traceback", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("correlation_id"),
    )


def downgrade() -> None:
    op.drop_table("rpc_responses_logs")
    op.drop_table("rpc_requests_logs")

"""Cascade delete RPC responses

Revision ID: 7a5a16c86789
Revises: 135a47ab3f0b
Create Date: 2025-01-29 14:20:33.007398

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "7a5a16c86789"
down_revision = "135a47ab3f0b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("rpc_responses_logs", schema=None) as batch_op:
        batch_op.drop_constraint(
            "fk_rpc_responses_logs_correlation_id_rpc_requests_logs", type_="foreignkey"
        )
        batch_op.create_foreign_key(
            batch_op.f("fk_rpc_responses_logs_correlation_id_rpc_requests_logs"),
            "rpc_requests_logs",
            ["correlation_id"],
            ["correlation_id"],
            ondelete="CASCADE",
        )


def downgrade() -> None:
    with op.batch_alter_table("rpc_responses_logs", schema=None) as batch_op:
        batch_op.drop_constraint(
            batch_op.f("fk_rpc_responses_logs_correlation_id_rpc_requests_logs"),
            type_="foreignkey",
        )
        batch_op.create_foreign_key(
            "fk_rpc_responses_logs_correlation_id_rpc_requests_logs",
            "rpc_requests_logs",
            ["correlation_id"],
            ["correlation_id"],
        )

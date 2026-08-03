"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-08-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    event_priority = postgresql.ENUM(
        "LOW", "MEDIUM", "HIGH", "CRITICAL", name="eventpriority"
    )
    nudge_channel = postgresql.ENUM(
        "WHATSAPP", "EMAIL", "SMS", "PUSH", name="nudgechannel"
    )
    nudge_status = postgresql.ENUM(
        "DELIVERED", "OPENED", "CLICKED", "REPLIED", "FAILED", name="nudgestatus"
    )

    event_priority.create(op.get_bind(), checkfirst=True)
    nudge_channel.create(op.get_bind(), checkfirst=True)
    nudge_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.String(), nullable=False, index=True),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("event_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "priority",
            postgresql.ENUM(
                "LOW", "MEDIUM", "HIGH", "CRITICAL", name="eventpriority", create_type=False
            ),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_events_user_id", "events", ["user_id"])

    op.create_table(
        "nudges",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.String(), nullable=False, index=True),
        sa.Column(
            "channel",
            postgresql.ENUM(
                "WHATSAPP", "EMAIL", "SMS", "PUSH", name="nudgechannel", create_type=False
            ),
            nullable=False,
        ),
        sa.Column("sent_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "DELIVERED",
                "OPENED",
                "CLICKED",
                "REPLIED",
                "FAILED",
                name="nudgestatus",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_nudges_user_id", "nudges", ["user_id"])

    op.create_table(
        "delivery_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "nudge_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("nudges.id"),
            nullable=False,
        ),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column(
            "report_time", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("meta", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("delivery_reports")
    op.drop_index("ix_nudges_user_id", table_name="nudges")
    op.drop_table("nudges")
    op.drop_index("ix_events_user_id", table_name="events")
    op.drop_table("events")

    postgresql.ENUM(name="nudgestatus").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="nudgechannel").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="eventpriority").drop(op.get_bind(), checkfirst=True)

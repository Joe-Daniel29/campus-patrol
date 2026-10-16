"""create zones, rovers, events and incidents

Revision ID: 0001
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "zones",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(80), nullable=False, unique=True),
        sa.Column("description", sa.Text, nullable=False, server_default=""),
        sa.Column("x", sa.Float, nullable=False, server_default="0"),
        sa.Column("y", sa.Float, nullable=False, server_default="0"),
        sa.Column("width", sa.Float, nullable=False, server_default="50"),
        sa.Column("height", sa.Float, nullable=False, server_default="50"),
    )
    op.create_table(
        "rovers",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(80), nullable=False, unique=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="IDLE"),
        sa.Column("battery", sa.Float, nullable=False, server_default="100"),
        sa.Column("x", sa.Float, nullable=False, server_default="0"),
        sa.Column("y", sa.Float, nullable=False, server_default="0"),
        sa.Column("heading", sa.Float, nullable=False, server_default="0"),
        sa.Column("last_seen", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "events",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("rover_id", sa.Integer, sa.ForeignKey("rovers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("zone_id", sa.Integer, sa.ForeignKey("zones.id", ondelete="SET NULL"), nullable=True),
        sa.Column("type", sa.String(40), nullable=False),
        sa.Column("severity", sa.String(10), nullable=False, server_default="INFO"),
        sa.Column("confidence", sa.Float, nullable=False, server_default="1"),
        sa.Column("message", sa.Text, nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_events_rover_id", "events", ["rover_id"])
    op.create_index("ix_events_created_at", "events", ["created_at"])
    op.create_table(
        "incidents",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("description", sa.Text, nullable=False, server_default=""),
        sa.Column("status", sa.String(20), nullable=False, server_default="OPEN"),
        sa.Column("severity", sa.String(10), nullable=False, server_default="WARNING"),
        sa.Column("assignee", sa.String(80), nullable=True),
        sa.Column("zone_id", sa.Integer, sa.ForeignKey("zones.id", ondelete="SET NULL"), nullable=True),
        sa.Column("event_id", sa.Integer, sa.ForeignKey("events.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_incidents_status", "incidents", ["status"])


def downgrade() -> None:
    op.drop_table("incidents")
    op.drop_table("events")
    op.drop_table("rovers")
    op.drop_table("zones")

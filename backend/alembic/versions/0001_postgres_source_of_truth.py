"""Postgres source of truth, audit trail, and evidence metadata."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001_postgres_sot"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "complaints",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tracking_id", sa.String(64), nullable=False, unique=True),
        sa.Column("owner_id", sa.String(64)),
        sa.Column("agency", sa.String(40), nullable=False),
        sa.Column("agency_reference", sa.String(120)),
        sa.Column("complaint_type", sa.String(160), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("consent_version", sa.String(32), nullable=False),
        sa.Column("consented_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_updated", sa.DateTime(timezone=True), nullable=False),
        sa.Column("next_action_at", sa.DateTime(timezone=True)),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failure_code", sa.String(80)),
    )
    op.create_index(
        "ix_complaints_tracking_id", "complaints", ["tracking_id"], unique=True
    )
    op.create_index("ix_complaints_owner_id", "complaints", ["owner_id"])
    op.create_index("ix_complaints_agency", "complaints", ["agency"])
    op.create_index("ix_complaints_status", "complaints", ["status"])
    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "tracking_id",
            sa.String(64),
            sa.ForeignKey("complaints.tracking_id"),
            nullable=False,
        ),
        sa.Column("event_type", sa.String(80), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
    )
    op.create_index("ix_events_tracking_id", "events", ["tracking_id"])
    op.create_index("ix_events_event_type", "events", ["event_type"])
    op.create_table(
        "evidence",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "tracking_id",
            sa.String(64),
            sa.ForeignKey("complaints.tracking_id"),
            nullable=False,
        ),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("content_type", sa.String(120), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("scan_status", sa.String(40), nullable=False),
        sa.Column("retention_until", sa.DateTime(timezone=True), nullable=False),
        sa.Column("content", sa.LargeBinary(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_evidence_tracking_id", "evidence", ["tracking_id"])


def downgrade() -> None:
    op.drop_table("evidence")
    op.drop_table("events")
    op.drop_table("complaints")

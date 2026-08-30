import json
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path
from threading import Lock
from typing import Any

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    create_engine,
    delete,
    select,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from .models import ComplaintState, ComplaintSubmission


class Base(DeclarativeBase):
    pass


class ComplaintRecord(Base):
    __tablename__ = "complaints"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tracking_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    owner_id: Mapped[str | None] = mapped_column(String(64), index=True)
    agency: Mapped[str] = mapped_column(String(40), index=True)
    agency_reference: Mapped[str | None] = mapped_column(String(120))
    complaint_type: Mapped[str] = mapped_column(String(160))
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSON)
    consent_version: Mapped[str] = mapped_column(String(32))
    consented_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(40), index=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    next_action_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    failure_code: Mapped[str | None] = mapped_column(String(80))


class AuditEvent(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tracking_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("complaints.tracking_id"), index=True
    )
    event_type: Mapped[str] = mapped_column(String(80), index=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)


class EvidenceRecord(Base):
    __tablename__ = "evidence"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tracking_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("complaints.tracking_id"), index=True
    )
    filename: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(120))
    size_bytes: Mapped[int] = mapped_column(Integer)
    scan_status: Mapped[str] = mapped_column(String(40))
    retention_until: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    content: Mapped[bytes] = mapped_column(LargeBinary)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


def _to_url(value: str | Path | None) -> str:
    if value is None:
        return os.getenv("DATABASE_URL", "sqlite:///backend/data/citizen-karen.db")
    text = str(value)
    if "://" in text:
        return text
    return f"sqlite:///{Path(text).resolve().as_posix()}"


class ComplaintStore:
    """Source-of-truth repository. Compose uses Postgres; tests use SQLite."""

    def __init__(self, database: str | Path | None = None):
        self.database_url = _to_url(database)
        connect_args = (
            {"check_same_thread": False}
            if self.database_url.startswith("sqlite")
            else {}
        )
        self.engine = create_engine(
            self.database_url, pool_pre_ping=True, connect_args=connect_args
        )
        self._lock = Lock()

    def init(self) -> None:
        Base.metadata.create_all(self.engine)

    def ready(self) -> bool:
        try:
            with Session(self.engine) as session:
                session.execute(select(1))
            return True
        except SQLAlchemyError:
            return False

    def create(
        self,
        *,
        complaint_id: str,
        tracking_id: str,
        submission: ComplaintSubmission,
        owner_id: str | None = None,
    ) -> dict[str, Any]:
        now = datetime.now(UTC)
        payload = submission.model_dump(mode="json", exclude={"consent", "website"})
        record = ComplaintRecord(
            id=complaint_id,
            tracking_id=tracking_id,
            owner_id=owner_id,
            agency=submission.agency,
            complaint_type=submission.complaint_type,
            payload_json=payload,
            consent_version=submission.consent_version,
            consented_at=now,
            status=ComplaintState.RECEIVED.value,
            submitted_at=now,
            last_updated=now,
            next_action_at=now + timedelta(days=14),
            retry_count=0,
        )
        with self._lock, Session(self.engine) as session, session.begin():
            session.add(record)
            # Flush the parent before append-only events. SQLite permits the unit-of-work
            # ordering implicitly; Postgres correctly enforces the tracking FK immediately.
            session.flush()
            self._event(
                session,
                tracking_id,
                "consent_recorded",
                now,
                {"version": submission.consent_version},
            )
            self._event(
                session,
                tracking_id,
                "complaint_received",
                now,
                {"agency": submission.agency},
            )
        return self.get(tracking_id) or {}

    def transition(
        self,
        tracking_id: str,
        state: str,
        *,
        event_type: str,
        agency_reference: str | None = None,
        failure_code: str | None = None,
        metadata: dict[str, Any] | None = None,
        increment_retry: bool = False,
    ) -> dict[str, Any] | None:
        allowed = {item.value for item in ComplaintState}
        normalized_state = state if state in allowed else ComplaintState.SUBMITTED.value
        now = datetime.now(UTC)
        with self._lock, Session(self.engine) as session, session.begin():
            record = session.scalar(
                select(ComplaintRecord).where(
                    ComplaintRecord.tracking_id == tracking_id
                )
            )
            if record is None:
                return None
            record.status = normalized_state
            record.last_updated = now
            if agency_reference is not None:
                record.agency_reference = agency_reference
            if failure_code is not None:
                record.failure_code = failure_code
            if increment_retry:
                record.retry_count += 1
            self._event(session, tracking_id, event_type, now, metadata)
        return self.get(tracking_id)

    def mark_submitted(
        self, tracking_id: str, *, agency_reference: str | None, state: str
    ) -> dict[str, Any] | None:
        return self.transition(
            tracking_id,
            state,
            event_type="submitted_to_agency",
            agency_reference=agency_reference,
            metadata={"agency_reference": agency_reference, "simulated": True},
        )

    def get(self, tracking_id: str) -> dict[str, Any] | None:
        with Session(self.engine) as session:
            record = session.scalar(
                select(ComplaintRecord).where(
                    ComplaintRecord.tracking_id == tracking_id
                )
            )
            if record is None:
                return None
            result = self._record_dict(record)
            events = session.scalars(
                select(AuditEvent)
                .where(AuditEvent.tracking_id == tracking_id)
                .order_by(AuditEvent.id)
            )
            result["events"] = [
                {
                    "type": event.event_type,
                    "occurred_at": event.occurred_at.isoformat(),
                    "metadata": event.metadata_json,
                }
                for event in events
            ]
            return result

    def list_cases(
        self, owner_id: str | None = None, limit: int = 100
    ) -> list[dict[str, Any]]:
        with Session(self.engine) as session:
            query = (
                select(ComplaintRecord)
                .order_by(ComplaintRecord.last_updated.desc())
                .limit(limit)
            )
            if owner_id:
                query = query.where(ComplaintRecord.owner_id == owner_id)
            return [self._record_dict(item) for item in session.scalars(query)]

    def delete_copy(self, tracking_id: str) -> bool:
        now = datetime.now(UTC)
        with self._lock, Session(self.engine) as session, session.begin():
            record = session.scalar(
                select(ComplaintRecord).where(
                    ComplaintRecord.tracking_id == tracking_id
                )
            )
            if record is None or record.deleted_at is not None:
                return False
            record.payload_json = {}
            record.complaint_type = "[deleted]"
            record.status = ComplaintState.DELETED.value
            record.deleted_at = now
            record.last_updated = now
            session.execute(
                delete(EvidenceRecord).where(EvidenceRecord.tracking_id == tracking_id)
            )
            self._event(session, tracking_id, "local_copy_deleted", now)
            return True

    def add_evidence(self, evidence: EvidenceRecord) -> None:
        with Session(self.engine) as session, session.begin():
            session.add(evidence)
            self._event(
                session,
                evidence.tracking_id,
                "evidence_scanned",
                evidence.created_at,
                {
                    "evidence_id": evidence.id,
                    "scan_status": evidence.scan_status,
                    "retention_until": evidence.retention_until.date().isoformat(),
                },
            )

    @staticmethod
    def _event(
        session: Session,
        tracking_id: str,
        event_type: str,
        occurred_at: datetime,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        session.add(
            AuditEvent(
                tracking_id=tracking_id,
                event_type=event_type,
                occurred_at=occurred_at,
                metadata_json=metadata or {},
            )
        )

    @staticmethod
    def _record_dict(record: ComplaintRecord) -> dict[str, Any]:
        return {
            "id": record.id,
            "tracking_id": record.tracking_id,
            "owner_id": record.owner_id,
            "agency": record.agency,
            "agency_reference": record.agency_reference,
            "complaint_type": record.complaint_type,
            "payload_json": json.dumps(record.payload_json, separators=(",", ":")),
            "consent_version": record.consent_version,
            "consented_at": record.consented_at.isoformat(),
            "status": record.status,
            "submitted_at": record.submitted_at.isoformat(),
            "last_updated": record.last_updated.isoformat(),
            "next_action_at": (
                record.next_action_at.isoformat() if record.next_action_at else None
            ),
            "deleted_at": record.deleted_at.isoformat() if record.deleted_at else None,
            "retry_count": record.retry_count,
            "failure_code": record.failure_code,
        }

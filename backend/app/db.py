import json
import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from collections.abc import Iterator
from typing import Any

from .models import ComplaintState, ComplaintSubmission


class ComplaintStore:
    """Durable Day-1 store with a narrow interface for later PostgreSQL migration."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._lock = Lock()

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path, check_same_thread=False)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def init(self) -> None:
        with self._lock, self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS complaints (
                    id TEXT PRIMARY KEY,
                    tracking_id TEXT UNIQUE NOT NULL,
                    agency TEXT NOT NULL,
                    agency_reference TEXT,
                    complaint_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    consent_version TEXT NOT NULL,
                    consented_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    submitted_at TEXT NOT NULL,
                    last_updated TEXT NOT NULL,
                    deleted_at TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_complaints_tracking_id
                    ON complaints(tracking_id);
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tracking_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    occurred_at TEXT NOT NULL,
                    metadata_json TEXT NOT NULL DEFAULT '{}'
                );
                """
            )

    def create(
        self,
        *,
        complaint_id: str,
        tracking_id: str,
        submission: ComplaintSubmission,
    ) -> dict[str, Any]:
        now = datetime.now(UTC).isoformat()
        payload = submission.model_dump(mode="json", exclude={"consent", "website"})
        with self._lock, self.connect() as connection:
            connection.execute(
                """
                INSERT INTO complaints (
                    id, tracking_id, agency, complaint_type, payload_json,
                    consent_version, consented_at, status, submitted_at, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    complaint_id,
                    tracking_id,
                    submission.agency,
                    submission.complaint_type,
                    json.dumps(payload, separators=(",", ":")),
                    submission.consent_version,
                    now,
                    ComplaintState.RECEIVED,
                    now,
                    now,
                ),
            )
            self._event(
                connection,
                tracking_id,
                "consent_recorded",
                now,
                {"version": submission.consent_version},
            )
            self._event(connection, tracking_id, "complaint_received", now)
        return self.get(tracking_id) or {}

    def mark_submitted(
        self, tracking_id: str, *, agency_reference: str | None, state: str
    ) -> dict[str, Any] | None:
        normalized_state = (
            state if state in {item.value for item in ComplaintState} else "submitted"
        )
        now = datetime.now(UTC).isoformat()
        with self._lock, self.connect() as connection:
            connection.execute(
                """
                UPDATE complaints
                SET status = ?, agency_reference = ?, last_updated = ?
                WHERE tracking_id = ? AND deleted_at IS NULL
                """,
                (normalized_state, agency_reference, now, tracking_id),
            )
            self._event(
                connection,
                tracking_id,
                "submitted_to_agency",
                now,
                {"agency_reference": agency_reference},
            )
        return self.get(tracking_id)

    def get(self, tracking_id: str) -> dict[str, Any] | None:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM complaints WHERE tracking_id = ?", (tracking_id,)
            ).fetchone()
        return dict(row) if row else None

    def delete_copy(self, tracking_id: str) -> bool:
        now = datetime.now(UTC).isoformat()
        with self._lock, self.connect() as connection:
            cursor = connection.execute(
                """
                UPDATE complaints
                SET payload_json = '{}', complaint_type = '[deleted]',
                    status = ?, deleted_at = ?, last_updated = ?
                WHERE tracking_id = ? AND deleted_at IS NULL
                """,
                (ComplaintState.DELETED, now, now, tracking_id),
            )
            if cursor.rowcount:
                self._event(connection, tracking_id, "local_copy_deleted", now)
            return bool(cursor.rowcount)

    @staticmethod
    def _event(
        connection: sqlite3.Connection,
        tracking_id: str,
        event_type: str,
        occurred_at: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        connection.execute(
            """
            INSERT INTO events (tracking_id, event_type, occurred_at, metadata_json)
            VALUES (?, ?, ?, ?)
            """,
            (
                tracking_id,
                event_type,
                occurred_at,
                json.dumps(metadata or {}, separators=(",", ":")),
            ),
        )

from __future__ import annotations

import sqlite3
from datetime import date
from pathlib import Path

from scraper.models import JobPosting


class JobRepository:
    def __init__(self, database_path: str):
        self.database_path = database_path

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        schema = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
        with self.connect() as connection:
            connection.executescript(schema)

    def upsert_many(self, jobs: list[JobPosting]) -> int:
        inserted = 0
        with self.connect() as connection:
            for job in jobs:
                params = (
                    job.dedupe_key,
                    job.source,
                    job.organization,
                    job.title,
                    job.job_name,
                    job.location,
                    job.employment_type,
                    _date_to_text(job.deadline),
                    _date_to_text(job.posted_at),
                    job.url,
                )
                cursor = connection.execute(
                    """
                    INSERT OR IGNORE INTO job_postings (
                        dedupe_key, source, organization, title, job_name, location,
                        employment_type, deadline, posted_at, url
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    params,
                )
                if cursor.rowcount == 1:
                    inserted += 1
                    continue

                connection.execute(
                    """
                    UPDATE job_postings
                    SET
                        last_seen_at = CURRENT_TIMESTAMP,
                        deadline = COALESCE(?, deadline),
                        posted_at = COALESCE(?, posted_at)
                    WHERE dedupe_key = ?
                    """,
                    (_date_to_text(job.deadline), _date_to_text(job.posted_at), job.dedupe_key),
                )
        return inserted

    def get_unsent_jobs(self) -> list[JobPosting]:
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM job_postings
                WHERE sent_at IS NULL
                ORDER BY
                    CASE WHEN deadline IS NULL THEN 1 ELSE 0 END,
                    deadline ASC,
                    organization ASC,
                    title ASC
                """
            ).fetchall()
        return [_row_to_job(row) for row in rows]

    def mark_as_sent(self, dedupe_keys: list[str]) -> None:
        if not dedupe_keys:
            return
        placeholders = ",".join("?" for _ in dedupe_keys)
        with self.connect() as connection:
            connection.execute(
                f"UPDATE job_postings SET sent_at = CURRENT_TIMESTAMP WHERE dedupe_key IN ({placeholders})",
                dedupe_keys,
            )


def _date_to_text(value: date | None) -> str | None:
    return value.isoformat() if value else None


def _text_to_date(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


def _row_to_job(row: sqlite3.Row) -> JobPosting:
    return JobPosting(
        source=row["source"],
        organization=row["organization"],
        title=row["title"],
        job_name=row["job_name"],
        location=row["location"],
        employment_type=row["employment_type"],
        deadline=_text_to_date(row["deadline"]),
        posted_at=_text_to_date(row["posted_at"]),
        url=row["url"],
    )

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import date
from urllib.parse import parse_qs, urlsplit


@dataclass(frozen=True)
class JobPosting:
    source: str
    organization: str
    title: str
    job_name: str | None
    location: str | None
    employment_type: str | None
    deadline: date | None
    posted_at: date | None
    url: str

    @property
    def dedupe_key(self) -> str:
        normalized_url = _canonical_url(self.url)
        raw = "|".join(
            [
                _normalize(self.organization),
                _normalize(self.title),
                self.deadline.isoformat() if self.deadline else "",
                normalized_url,
            ]
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _normalize(value: str | None) -> str:
    return re.sub(r"\s+", "", value or "").lower()


def _canonical_url(url: str) -> str:
    parsed = urlsplit(url)
    query = parse_qs(parsed.query)
    for key in ["rec_idx", "gno", "GI_No", "empSeqno", "wantedAuthNo"]:
        if query.get(key):
            return f"{parsed.netloc}{parsed.path}?{key}={query[key][0]}"
    return f"{parsed.netloc}{parsed.path}".rstrip("/")

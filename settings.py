from __future__ import annotations

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv


DEFAULT_KEYWORDS = [
    "평생교육사",
    "평생교육",
    "평생학습",
    "교육기획",
    "교육운영",
    "교육코디네이터",
    "학습매니저",
    "교육사업",
    "교육행정",
]


@dataclass(frozen=True)
class Settings:
    database_path: str = "database/job_radar.sqlite3"
    reports_dir: str = "reports"
    sources_path: str = "sources.json"
    resend_api_key: str | None = None
    email_to: str | None = "oncontents@gmail.com"
    email_from: str = "Job Radar <onboarding@resend.dev>"
    request_timeout: int = 15
    user_agent: str = "Mozilla/5.0 (compatible; LifelongEducatorJobRadar/1.0)"
    keywords: list[str] = field(default_factory=lambda: DEFAULT_KEYWORDS.copy())

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        keywords = os.getenv("JOB_KEYWORDS")
        parsed_keywords = [k.strip() for k in keywords.split(",") if k.strip()] if keywords else DEFAULT_KEYWORDS
        return cls(
            database_path=os.getenv("DATABASE_PATH", cls.database_path),
            reports_dir=os.getenv("REPORTS_DIR", cls.reports_dir),
            sources_path=os.getenv("SOURCES_PATH", cls.sources_path),
            resend_api_key=os.getenv("RESEND_API_KEY"),
            email_to=os.getenv("EMAIL_TO", cls.email_to),
            email_from=os.getenv("EMAIL_FROM", cls.email_from),
            request_timeout=int(os.getenv("REQUEST_TIMEOUT", cls.request_timeout)),
            user_agent=os.getenv("USER_AGENT", cls.user_agent),
            keywords=parsed_keywords,
        )

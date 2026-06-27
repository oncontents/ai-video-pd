from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit

from scraper.base import BaseScraper
from scraper.models import JobPosting
from scraper.utils import absolutize, clean_text, fetch_soup, infer_job_name, parse_date


logger = logging.getLogger(__name__)

URL_FIELDS = ["recruitment_url", "notice_url", "job_board_url"]


class PublicSiteScraper(BaseScraper):
    source_name = "평생교육기관"

    def fetch(self) -> list[JobPosting]:
        jobs: dict[str, JobPosting] = {}
        for source in self._load_sources():
            institution_name = clean_text(source.get("institution_name")) or "기관명 미확인"
            for page_url in self._source_urls(source):
                try:
                    soup = fetch_soup(
                        page_url,
                        timeout=self.settings.request_timeout,
                        user_agent=self.settings.user_agent,
                    )
                except Exception as exc:
                    logger.warning("Institution page skipped: %s %s (%s)", institution_name, page_url, exc)
                    continue

                for link in soup.select("a[href]"):
                    text = clean_text(link.get_text(" "))
                    if not self._looks_like_job_posting(text):
                        continue

                    url = absolutize(page_url, link.get("href"))
                    posting = JobPosting(
                        source=institution_name,
                        organization=institution_name,
                        title=text[:200],
                        job_name=infer_job_name(text, self.settings.keywords),
                        location=None,
                        employment_type=None,
                        deadline=parse_date(text),
                        posted_at=None,
                        url=url,
                    )
                    jobs[posting.dedupe_key] = posting
        return sorted(jobs.values(), key=lambda job: (job.deadline or datetime.max.date(), job.title))

    def _load_sources(self) -> list[dict[str, str]]:
        path = Path(self.settings.sources_path)
        if not path.exists():
            logger.warning("sources.json not found: %s", path)
            return []

        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            return payload
        return payload.get("institutions", [])

    def _source_urls(self, source: dict[str, str]) -> list[str]:
        urls: list[str] = []
        seen: set[str] = set()
        for field in URL_FIELDS:
            url = clean_text(source.get(field))
            if not url or url in seen:
                continue
            parsed = urlsplit(url)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                logger.warning("Invalid URL skipped: %s=%s", field, url)
                continue
            urls.append(url)
            seen.add(url)
        return urls

    def _looks_like_job_posting(self, text: str) -> bool:
        if not text:
            return False
        job_tokens = ["채용", "모집", "공고", "임용", "직원", "기간제", "계약직"]
        return any(keyword in text for keyword in self.settings.keywords) or any(token in text for token in job_tokens)

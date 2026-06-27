from __future__ import annotations

from datetime import datetime

from scraper.base import BaseScraper
from scraper.models import JobPosting
from scraper.utils import absolutize, clean_text, fetch_soup, infer_job_name, keyword_search_url, parse_date


class JobKoreaScraper(BaseScraper):
    source_name = "잡코리아"
    search_url = "https://www.jobkorea.co.kr/Search/?stext={keyword}"

    def fetch(self) -> list[JobPosting]:
        jobs: dict[str, JobPosting] = {}
        for keyword in self.settings.keywords:
            soup = fetch_soup(
                keyword_search_url(self.search_url, keyword),
                timeout=self.settings.request_timeout,
                user_agent=self.settings.user_agent,
            )
            for item in soup.select(".list-post, .post, .recruit-info, tr"):
                text = clean_text(item.get_text(" "))
                if keyword not in text:
                    continue
                link = item.select_one("a[href*='/Recruit/GI_Read'], a[href]")
                title = clean_text(link.get_text(" ")) if link else text[:80]
                company = item.select_one(".name, .corp, .company")
                organization = clean_text(company.get_text(" ")) if company else "기관명 미확인"
                posting = JobPosting(
                    source=self.source_name,
                    organization=organization[:120],
                    title=title[:200],
                    job_name=infer_job_name(title + " " + text, self.settings.keywords),
                    location=None,
                    employment_type=None,
                    deadline=parse_date(text),
                    posted_at=None,
                    url=absolutize("https://www.jobkorea.co.kr", link.get("href") if link else None),
                )
                jobs[posting.dedupe_key] = posting
        return sorted(jobs.values(), key=lambda job: (job.deadline or datetime.max.date(), job.title))

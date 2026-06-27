from __future__ import annotations

from datetime import datetime

from scraper.base import BaseScraper
from scraper.models import JobPosting
from scraper.utils import absolutize, clean_text, fetch_soup, infer_job_name, keyword_search_url, parse_date


class WorknetScraper(BaseScraper):
    source_name = "워크넷"
    search_url = "https://www.work.go.kr/empInfo/empInfoSrch/list/dtlEmpSrchList.do?keyword={keyword}"

    def fetch(self) -> list[JobPosting]:
        jobs: dict[str, JobPosting] = {}
        for keyword in self.settings.keywords:
            soup = fetch_soup(
                keyword_search_url(self.search_url, keyword),
                timeout=self.settings.request_timeout,
                user_agent=self.settings.user_agent,
            )
            for row in soup.select("tr, li, .cp-info-in, .job-list, .recruitInfo"):
                text = clean_text(row.get_text(" "))
                if keyword not in text:
                    continue
                link = row.select_one("a[href]")
                title = clean_text(link.get_text(" ")) if link else text[:80]
                url = absolutize("https://www.work.go.kr", link.get("href") if link else None)
                organization = clean_text((row.select_one(".company, .cp-name, .corp") or row).get_text(" "))
                deadline = parse_date(text)
                posting = JobPosting(
                    source=self.source_name,
                    organization=organization[:120] or "기관명 미확인",
                    title=title[:200],
                    job_name=infer_job_name(title + " " + text, self.settings.keywords),
                    location=None,
                    employment_type=None,
                    deadline=deadline,
                    posted_at=None,
                    url=url,
                )
                jobs[posting.dedupe_key] = posting
        return sorted(jobs.values(), key=lambda job: (job.deadline or datetime.max.date(), job.title))

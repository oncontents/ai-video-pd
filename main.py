from __future__ import annotations

import logging
from pathlib import Path

from database.repository import JobRepository
from notifiers.resend_email import ResendEmailClient
from reports.markdown import build_markdown_report, save_report
from scraper.models import JobPosting
from scraper.sources import get_default_scrapers
from settings import Settings


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)

logger = logging.getLogger("job-radar")


def collect_jobs(settings: Settings) -> list[JobPosting]:
    jobs: list[JobPosting] = []
    for scraper in get_default_scrapers(settings):
        try:
            source_jobs = scraper.fetch()
            logger.info("%s collected %s postings", scraper.source_name, len(source_jobs))
            jobs.extend(source_jobs)
        except Exception:
            logger.exception("%s scraper failed", scraper.source_name)
    return jobs


def main() -> None:
    settings = Settings.from_env()
    Path(settings.reports_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.database_path).parent.mkdir(parents=True, exist_ok=True)

    repository = JobRepository(settings.database_path)
    repository.initialize()

    collected_jobs = collect_jobs(settings)
    inserted_jobs = repository.upsert_many(collected_jobs)
    new_jobs = repository.get_unsent_jobs()

    report = build_markdown_report(new_jobs)
    report_path = save_report(report, settings.reports_dir)

    logger.info("Collected=%s Inserted=%s New unsent=%s", len(collected_jobs), inserted_jobs, len(new_jobs))
    logger.info("Report saved: %s", report_path)

    if new_jobs and settings.resend_api_key and settings.email_to:
        ResendEmailClient(settings).send_markdown(
            subject=f"오늘의 평생교육사 채용정보 - 신규 {len(new_jobs)}건",
            markdown_body=report,
        )
        repository.mark_as_sent([job.dedupe_key for job in new_jobs])
        logger.info("Email sent to %s", settings.email_to)
    elif not new_jobs:
        logger.info("No new postings. Email skipped.")
    else:
        logger.warning("RESEND_API_KEY or EMAIL_TO missing. Email skipped.")


if __name__ == "__main__":
    main()

from __future__ import annotations

from scraper.base import BaseScraper
from scraper.jobkorea import JobKoreaScraper
from scraper.public_sites import PublicSiteScraper
from scraper.saramin import SaraminScraper
from scraper.worknet import WorknetScraper
from settings import Settings


def get_default_scrapers(settings: Settings) -> list[BaseScraper]:
    return [
        WorknetScraper(settings),
        SaraminScraper(settings),
        JobKoreaScraper(settings),
        PublicSiteScraper(settings),
    ]

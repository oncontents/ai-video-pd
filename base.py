from __future__ import annotations

from abc import ABC, abstractmethod

from scraper.models import JobPosting
from settings import Settings


class BaseScraper(ABC):
    source_name: str

    def __init__(self, settings: Settings):
        self.settings = settings

    @abstractmethod
    def fetch(self) -> list[JobPosting]:
        raise NotImplementedError

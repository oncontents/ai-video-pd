from __future__ import annotations

import logging
import re
from datetime import date, datetime
from urllib.parse import quote_plus, urljoin

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def fetch_soup(url: str, *, timeout: int, user_agent: str) -> BeautifulSoup:
    response = requests.get(url, timeout=timeout, headers={"User-Agent": user_agent})
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def absolutize(base_url: str, href: str | None) -> str:
    if not href:
        return base_url
    return urljoin(base_url, href)


def clean_text(value: str | None) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def parse_date(value: str | None) -> date | None:
    text = clean_text(value)
    if not text or any(token in text for token in ["상시", "채용시", "수시"]):
        return None

    patterns = [
        r"(20\d{2})[.\-/년\s]+(\d{1,2})[.\-/월\s]+(\d{1,2})",
        r"(\d{2})[.\-/](\d{1,2})[.\-/](\d{1,2})",
        r"(\d{1,2})[.\-/](\d{1,2})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if not match:
            continue
        groups = match.groups()
        try:
            if len(groups) == 3:
                year = int(groups[0])
                if year < 100:
                    year += 2000
                return date(year, int(groups[1]), int(groups[2]))
            return date(datetime.now().year, int(groups[0]), int(groups[1]))
        except ValueError:
            logger.debug("Unable to parse date: %s", value)
    return None


def keyword_search_url(base_url: str, keyword: str) -> str:
    return base_url.format(keyword=quote_plus(keyword))


def infer_job_name(title: str, keywords: list[str]) -> str | None:
    for keyword in keywords:
        if keyword in title:
            return keyword
    return None

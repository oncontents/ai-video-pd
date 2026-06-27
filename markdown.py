from __future__ import annotations

from collections import Counter
from datetime import datetime
from pathlib import Path

from scraper.models import JobPosting


def build_markdown_report(jobs: list[JobPosting]) -> str:
    lines = [
        "# 오늘의 평생교육사 채용정보",
        "",
        f"생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        f"## 신규 공고 {len(jobs)}건",
        "",
    ]

    if not jobs:
        lines.extend(["신규 채용공고가 없습니다.", ""])
    else:
        for job in jobs:
            lines.extend(
                [
                    f"### {job.organization}",
                    "",
                    f"* 제목: {job.title}",
                    f"* 직무: {job.job_name or '확인 필요'}",
                    f"* 지역: {job.location or '확인 필요'}",
                    f"* 고용형태: {job.employment_type or '확인 필요'}",
                    f"* 마감일: {job.deadline.isoformat() if job.deadline else '상시/확인 필요'}",
                    f"* 등록일: {job.posted_at.isoformat() if job.posted_at else '확인 필요'}",
                    f"* 출처: {job.source}",
                    f"* 링크: {job.url}",
                    "",
                ]
            )

    location_counts = Counter(job.location or "확인 필요" for job in jobs)
    keyword_counts = Counter(job.job_name or "확인 필요" for job in jobs)

    lines.extend(
        [
            "# 채용시장 요약",
            "",
            f"* 신규 공고 수: {len(jobs)}건",
            f"* 지역별 분포: {_format_counter(location_counts)}",
            f"* 가장 많이 등장한 직무 키워드: {_format_counter(keyword_counts)}",
            "",
        ]
    )
    return "\n".join(lines)


def save_report(markdown: str, reports_dir: str) -> Path:
    path = Path(reports_dir) / f"job_report_{datetime.now().strftime('%Y%m%d')}.md"
    path.write_text(markdown, encoding="utf-8")
    return path


def _format_counter(counter: Counter[str]) -> str:
    if not counter:
        return "없음"
    return ", ".join(f"{key} {count}건" for key, count in counter.most_common(5))

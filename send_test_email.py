from __future__ import annotations

import logging

from dotenv import load_dotenv

from notifiers.resend_email import ResendEmailClient
from settings import Settings


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)

logger = logging.getLogger("job-radar-test-email")


def main() -> None:
    load_dotenv()
    settings = Settings.from_env()

    if not settings.resend_api_key:
        raise SystemExit(
            "RESEND_API_KEY가 없습니다. .env 파일 또는 GitHub Secrets에 RESEND_API_KEY를 먼저 설정하세요."
        )

    if not settings.email_to:
        raise SystemExit("EMAIL_TO가 없습니다. 기본값은 oncontents@gmail.com입니다.")

    ResendEmailClient(settings).send_markdown(
        subject="평생교육사 채용 레이더 테스트 메일",
        markdown_body=(
            "# 테스트 메일\n\n"
            "이 메일이 도착했다면 Resend API와 수신 메일 설정은 정상입니다.\n\n"
            f"* 수신자: {settings.email_to}\n"
            f"* 발신자: {settings.email_from}\n"
        ),
    )
    logger.info("Test email sent to %s", settings.email_to)


if __name__ == "__main__":
    main()

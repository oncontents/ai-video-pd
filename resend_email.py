from __future__ import annotations

import requests

from settings import Settings


class ResendEmailClient:
    endpoint = "https://api.resend.com/emails"

    def __init__(self, settings: Settings):
        self.settings = settings

    def send_markdown(self, *, subject: str, markdown_body: str) -> None:
        if not self.settings.resend_api_key or not self.settings.email_to:
            raise ValueError("RESEND_API_KEY and EMAIL_TO are required.")

        response = requests.post(
            self.endpoint,
            headers={
                "Authorization": f"Bearer {self.settings.resend_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "from": self.settings.email_from,
                "to": [self.settings.email_to],
                "subject": subject,
                "text": markdown_body,
            },
            timeout=self.settings.request_timeout,
        )
        response.raise_for_status()

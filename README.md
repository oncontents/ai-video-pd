# 평생교육사 채용 레이더

매일 오전 8시(KST)에 평생교육사 관련 채용공고를 수집하고, 신규 공고만 Markdown 리포트와 이메일로 발송하는 자동화 프로젝트입니다.

## 핵심 기능

* 워크넷, 사람인, 잡코리아, 주요 평생교육 기관 사이트 검색
* SQLite 기반 중복 제거 및 재발송 방지
* 마감일 오름차순 Markdown 리포트 생성
* Resend API 이메일 발송
* GitHub Actions 매일 자동 실행
* Notion, Telegram 확장을 고려한 모듈형 구조

## 설치

```bash
cd job-radar
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Windows PowerShell에서는 다음을 사용합니다.

```powershell
cd job-radar
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

## 환경변수

`.env` 파일을 열어 아래 값을 설정합니다.

```env
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxx
EMAIL_TO=oncontents@gmail.com
EMAIL_FROM=Job Radar <onboarding@resend.dev>
DATABASE_PATH=database/job_radar.sqlite3
REPORTS_DIR=reports
SOURCES_PATH=sources.json
```

Resend 기본 발신자인 `onboarding@resend.dev`는 테스트용입니다. 운영 발송은 Resend에서 인증한 도메인 발신자로 교체하는 것이 좋습니다.

## 실행

```bash
python main.py
```

실행 결과:

* `database/job_radar.sqlite3`: 수집 이력, 중복 제거, 발송 이력 저장
* `reports/job_report_YYYYMMDD.md`: 당일 Markdown 리포트 생성
* 신규 공고가 있고 이메일 환경변수가 설정된 경우 Resend로 이메일 발송

## GitHub Actions 설정

`.github/workflows/job_radar.yml`은 UTC 23:00에 실행됩니다. 한국시간으로 매일 오전 8시입니다.

GitHub 저장소에서 다음 Secret을 등록합니다.

* `RESEND_API_KEY`
* `EMAIL_TO` - 생략하면 `oncontents@gmail.com`으로 발송합니다.

선택적으로 Repository Variable을 등록합니다.

* `EMAIL_FROM`

이메일이 오지 않을 때는 [EMAIL_SETUP.md](EMAIL_SETUP.md)를 먼저 따라가며 `send_test_email.py`로 메일 발송만 따로 확인합니다.

메일이 오지 않으면 먼저 Actions 실행 로그에서 아래 문구를 확인합니다.

* `RESEND_API_KEY or EMAIL_TO missing. Email skipped.`: `RESEND_API_KEY` secret이 없어서 발송이 건너뛰어진 상태입니다.
* `No new postings. Email skipped.`: 신규 공고가 없어 발송하지 않은 상태입니다.
* `Email sent to oncontents@gmail.com`: Resend API 발송 요청은 성공한 상태입니다. 이 경우 Gmail 스팸함과 Resend 대시보드의 delivery 상태를 확인합니다.

## 데이터베이스 스키마

스키마는 `database/schema.sql`에 있습니다.

핵심 컬럼:

* `dedupe_key`: 출처, 기관명, 제목, URL 기반 중복 제거 키
* `first_seen_at`: 최초 수집 시각
* `last_seen_at`: 마지막 확인 시각
* `sent_at`: 이메일 발송 시각. 값이 있으면 재발송하지 않습니다.

## 기관 목록 관리

전국 평생학습관 및 평생교육기관 수집 대상은 `sources.json`에서 관리합니다. 코드 수정 없이 JSON에 기관을 추가하면 다음 실행부터 자동으로 반영됩니다.

```json
{
  "institution_name": "기관명",
  "recruitment_url": "https://example.org/recruit",
  "notice_url": "https://example.org/notice",
  "job_board_url": "https://example.org/jobs"
}
```

각 기관은 `recruitment_url`, `notice_url`, `job_board_url`을 순회하며, 링크 텍스트에 `채용`, `모집`, `공고`, `임용`, `직원`, `기간제`, `계약직` 또는 검색 키워드가 포함되면 후보 공고로 저장합니다.

## 운영상 주의점

채용 플랫폼은 HTML 구조와 접근 정책이 바뀔 수 있습니다. 스크레이퍼는 실패해도 전체 실행이 중단되지 않도록 설계했지만, 특정 사이트의 결과가 갑자기 줄면 해당 사이트의 CSS selector를 점검해야 합니다.

GitHub Actions는 실행 환경이 매번 새로 만들어지므로 workflow에서 `actions/cache`로 `database/job_radar.sqlite3`를 복원/저장하도록 구성했습니다. 다만 GitHub cache는 장기 운영용 데이터베이스가 아니므로, 운영 규모가 커지면 다음 중 하나로 이전하는 것이 좋습니다.

* Supabase, Neon, Turso 같은 외부 DB로 확장
* S3/R2 같은 오브젝트 스토리지에 SQLite 백업
* Notion DB를 수집 이력 저장소로 함께 사용

## 확장 방향

요청 구조의 `email/` 폴더명은 유지했지만, Python 표준 라이브러리 `email`과 충돌을 피하기 위해 실제 발송 모듈은 `notifiers/resend_email.py`에서 import합니다.

Notion 연동은 `notifiers/` 또는 별도 `integrations/notion.py` 모듈로 추가하고, `dedupe_key`를 Notion DB의 고유 키로 사용하면 됩니다.

Telegram 알림은 `notifiers/base.py`의 `Notifier` 인터페이스를 구현해 신규 공고 요약만 발송하는 방식이 적합합니다.

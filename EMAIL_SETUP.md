# 이메일 발송 설정 가이드

이 프로젝트는 Resend라는 이메일 발송 서비스를 사용합니다. Gmail 주소를 받는 메일로 쓰는 것은 가능하지만, 보내는 쪽은 Resend API 키가 반드시 필요합니다.

## 1. 가장 먼저 확인할 것

현재 코드의 기본 수신자는 `oncontents@gmail.com`입니다.

하지만 아래 값이 없으면 메일은 절대 발송되지 않습니다.

```env
RESEND_API_KEY=...
```

## 2. 로컬에서 테스트하는 방법

프로젝트 폴더에 `.env` 파일을 만들고 아래처럼 입력합니다.

```env
RESEND_API_KEY=Resend에서_발급받은_API_KEY
EMAIL_TO=oncontents@gmail.com
EMAIL_FROM=Job Radar <onboarding@resend.dev>
```

그 다음 메일만 테스트합니다.

```bash
python send_test_email.py
```

성공하면 로그에 아래처럼 표시됩니다.

```text
Test email sent to oncontents@gmail.com
```

## 3. GitHub Actions에서 설정하는 방법

GitHub 저장소에서 다음 순서로 이동합니다.

1. `Settings`
2. `Secrets and variables`
3. `Actions`
4. `New repository secret`

아래 Secret을 추가합니다.

| Name | Value |
| --- | --- |
| `RESEND_API_KEY` | Resend에서 발급받은 API 키 |

`EMAIL_TO`는 등록하지 않아도 기본값 `oncontents@gmail.com`으로 발송됩니다.

## 4. 수동 실행 확인

GitHub 저장소에서 다음 순서로 이동합니다.

1. `Actions`
2. `Lifelong Educator Job Radar`
3. `Run workflow`

실행 로그에서 아래 문구를 확인합니다.

| 로그 문구 | 의미 |
| --- | --- |
| `Email sent to oncontents@gmail.com` | 발송 요청 성공 |
| `RESEND_API_KEY or EMAIL_TO missing. Email skipped.` | API 키가 없어 발송 안 됨 |
| `No new postings. Email skipped.` | 신규 공고가 없어 발송 안 됨 |

## 5. 발송 성공인데 Gmail에 없을 때

Gmail에서 아래를 확인합니다.

1. 스팸함
2. 프로모션함
3. 전체보관함
4. Gmail 검색창에 `from:onboarding@resend.dev` 입력

Resend 대시보드에서도 이메일 delivery 상태를 확인합니다.

## 6. 운영 권장 설정

`onboarding@resend.dev`는 테스트용 발신자입니다. 안정적으로 보내려면 Resend에서 본인 도메인을 인증하고 `EMAIL_FROM`을 인증된 주소로 바꾸는 것이 좋습니다.

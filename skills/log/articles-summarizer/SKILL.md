---
name: articles-summarizer
description: This skill should be used when the user wants to summarize multiple web documents or GitHub links. It fetches content from provided URLs (web articles, blog posts, GitHub PRs/issues), generates Korean summaries with hierarchical structure (3-5 core topics with 2-4 bullet points each), and saves each summary as a separate Markdown file in the user's Obsidian vault with proper frontmatter and content-based tags.
argument-hint: "[url1] [url2] ... | --ask <filename> \"<question>\""
allowed-tools:
  - WebFetch
  - Bash
  - Write
  - Read
---

# Articles Summarizer

여러 웹 링크(URL, GitHub PR/Issue)를 각각 한국어로 요약해 Obsidian vault에 개별 파일로 저장한다.
파일명·저장 경로·중복 처리는 자동 — 사용자 확인 없이 즉시 처리하고 결과 리포트만 출력한다.

- **저장 경로**: `/Users/choiyoungjun/Documents/Obsidian Vault/articles/2026`
- **호출**: `/articles-summarizer <url1> <url2> ...` 또는 대화 중 "이 링크들 요약해줘" (최대 20개)

## Workflow

### 1. 링크 수집·검증

URL 파싱·검증·타입 분류·중복 제거·파일명 생성은 `scripts/link_utils.py`의 함수를 사용한다
(`parse_links_from_text`, `classify_link`, `generate_filename`, `remove_duplicates` 등).
직접 규칙을 재구현하지 말 것 — 파일명 규칙(도메인 축약, sanitize, GitHub `github-{owner}-{repo}-{번호}` 형식)의
정본은 이 스크립트다. 예:

```bash
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from link_utils import parse_links_from_text, classify_link, generate_filename
..."
```

### 2. 콘텐츠 가져오기

- 일반 웹 URL → `WebFetch` (5개 이하 병렬, 6개 이상은 5개씩 배치)
- GitHub PR/Issue → `gh pr view` / `gh issue view` (rate limit 시 WebFetch로 폴백)
- 접근 실패 시 1회 재시도 후 스킵하고 실패 목록에 기록. 나머지는 계속 진행

### 3. 요약 생성

각 문서를 `assets/template.md` 구조로 요약한다 (형식 정본은 템플릿 — 여기 재서술하지 않음):

- 핵심 주제 3~5개(H3) × 상세 bullet 2~4개, 항상 한국어
- 기술 문서면 핵심 코드 예제 2~3개만 `## 주요 코드 예제`에 포함, 아니면 섹션 생략
- frontmatter `tags`: 내용 기반 3~7개, kebab-case
- frontmatter `type`: `web-article` | `github-pr` | `github-issue` (100단어 미만 문서는 전문 수록 + `short-content`)

### 4. 저장·리포트

파일명 충돌 시 타임스탬프 suffix를 붙여 새 파일로 저장(`link_utils.add_timestamp_suffix`).
저장 실패 시 해당 요약을 터미널에 백업 출력하고 나머지는 계속.

```
✅ 요약 완료 (N/M)
성공: <파일명 목록>
실패: <URL — 사유>
```

## Ask Mode (기존 요약에 추가 질문)

```
/articles-summarizer --ask <파일명> "<질문>"
```

1. vault에서 파일명(부분 일치 허용, 복수 매칭 시 최신 파일)으로 요약 파일 검색
2. frontmatter의 `url`로 원문을 다시 WebFetch (실패 시 요약 내용만으로 답변)
3. 질문에 한국어로 답변 — 터미널 출력만, 파일 저장 없음

## Resources

- `scripts/link_utils.py` — URL 검증·분류·파일명 생성·배치·중복 제거 (정본)
- `assets/template.md` — 저장 파일 형식 (정본)

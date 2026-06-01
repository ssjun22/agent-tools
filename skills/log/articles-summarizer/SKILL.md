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

## Overview

여러 웹 링크(URL, GitHub)를 입력받아 각 문서를 개별적으로 요약하여 Obsidian vault에 저장하는 스킬입니다. 각 요약은 한국어로 작성되며, 계층적 구조(핵심 내용 + 상세 설명)로 정리됩니다.

**사용법**:
- 커맨드와 함께 URL 전달: `/articles-summarizer <url1> <url2> ...`
- 또는 대화 중에 링크 제공: "이 링크들 요약해줘: <urls>"

링크가 `$ARGUMENTS`로 전달된 경우 해당 인자를 파싱하여 처리합니다.

**자동 처리 원칙**:
- 파일명, 저장 경로, 중복 처리 등 모든 과정이 자동으로 진행됩니다
- 사용자 확인이나 추가 입력 없이 즉시 요약을 생성하고 저장합니다
- 처리 완료 후 결과 리포트만 제공합니다

## When to Use This Skill

다음과 같은 상황에서 이 스킬을 사용합니다:

**요약 생성 모드**:
- 사용자가 "여러 링크 요약해줘", "이 문서들 정리해줘" 등을 요청할 때
- 여러 URL(최대 20개)과 함께 요약 요청이 들어올 때
- GitHub PR이나 Issue 링크의 내용을 정리하고 싶을 때
- Obsidian vault에 정리된 요약 문서를 생성하고 싶을 때

**추가 질문 모드**:
- 이미 생성된 요약 문서에 대해 더 자세한 정보가 필요할 때
- 파일명만 제공하여 원문에 대해 질문할 때
- 예: `/articles-summarizer --ask velog-react-useeffect "useEffectEvent는 어떻게 동작하나요?"`

## Ask Mode (추가 질문 기능)

이미 요약된 문서에 대해 추가 질문을 할 수 있습니다.

**사용법**:
```
/articles-summarizer --ask <파일명> "<질문>"
```

**예시**:
```
/articles-summarizer --ask velog-react-useeffect "useEffectEvent의 구체적인 사용 예제는?"
/articles-summarizer --ask github-pr-anthropics-claude-1234 "이 PR의 주요 변경 사항은?"
```

**처리 과정**:
1. 파일명을 기반으로 Obsidian vault에서 요약 파일 찾기
2. 파일의 frontmatter에서 원본 URL 추출
3. 원본 URL로 WebFetch하여 최신 콘텐츠 가져오기
4. 사용자 질문에 대한 답변 생성 (한국어)
5. 답변만 터미널에 출력 (파일 저장 안 함)

**참고**:
- 파일명은 확장자(.md) 없이 입력 가능
- 파일명의 일부만 입력해도 매칭 시도
- 여러 파일이 매칭되면 가장 최근 파일 사용
- 원본 URL 접근 실패 시 요약 파일 내용만으로 답변

## Workflow

### 1. 링크 수집 및 검증

사용자로부터 링크를 입력받습니다:
- 공백 또는 줄바꿈으로 구분된 URL 목록
- 최대 20개까지 처리 가능
- 지원하는 링크 타입:
  - 웹 URL: `http://` 또는 `https://`로 시작
  - GitHub PR: `github.com/.../pull/`
  - GitHub Issue: `github.com/.../issues/`

링크 검증:
- URL 형식 확인
- 중복 링크 제거 (동일 URL 여러 번 입력 시)
- 링크 타입별 분류 (웹 vs GitHub)

### 2. 콘텐츠 가져오기

링크 개수에 따라 자동으로 처리 전략을 선택합니다:
- **5개 이하**: 병렬로 모두 가져오기
- **6개 이상**: 5개씩 배치로 나누어 처리

도구 사용:
- 일반 웹 URL → `WebFetch` 도구 사용
- GitHub 링크 → `gh` CLI 사용 (예: `gh pr view`, `gh issue view`)

에러 처리:
- 접근 실패 시 1회 재시도 (5초 대기)
- 재시도 실패 시 해당 링크 스킵, 실패 목록에 추가
- 나머지 링크는 계속 처리

### 3. 요약 생성

각 문서를 순차적으로 처리하여 한국어 요약을 생성합니다.

**요약 구조**:
- 3-5개의 핵심 주제/내용 (H3 헤더)
- 각 핵심 내용당 2-4개의 상세 설명 bullets
- 총 10-20개 bullets
- 기술 문서의 경우 주요 코드 예제 섹션 추가

**예시**:
```markdown
## 요약

### Claude 4.0의 새로운 기능
- 컨텍스트 윈도우가 200K 토큰으로 확장
- 멀티모달 입력 지원 강화 (이미지, PDF)
- 응답 속도 30% 향상

### 성능 개선 사항
- 코드 생성 정확도 향상
- 복잡한 추론 작업 처리 능력 개선

## 주요 코드 예제
(기술 문서에 중요한 코드가 있는 경우)

\`\`\`javascript
// 예제 코드
const example = () => {
  // 설명과 함께 제공
}
\`\`\`
```

**코드 블록 포함 기준**:
- 기술 문서(프로그래밍, API, 라이브러리 등)인 경우
- 문서에서 핵심 개념을 설명하는 코드 예제가 있는 경우
- 최대 2-3개의 중요한 코드 스니펫만 포함
- 각 코드 블록에 간단한 설명 추가

**태그 추출**:
- 문서 내용에서 3-7개의 주요 키워드/주제 자동 추출
- 기술 스택, 도메인, 카테고리 등 실제 검색에 유용한 태그
- kebab-case 형식 사용 (예: `ai`, `machine-learning`, `react`)

### 4. 파일명 생성

URL을 기반으로 자동으로 파일명을 생성합니다:

**일반 웹 문서**: `{도메인}-{제목-slug}.md`
- 예: `nytimes-ai-breakthrough-2026.md`
- 예: `techcrunch-startup-funding-round.md`

**GitHub PR**: `github-pr-{repo}-{number}.md`
- 예: `github-pr-anthropics-claude-1234.md`

**GitHub Issue**: `github-issue-{repo}-{number}.md`
- 예: `github-issue-facebook-react-5678.md`

**복잡한 경우**:
- URL이 너무 길거나 특수문자가 많은 경우
- 자동으로 `{source}-{timestamp}.md` 형식 사용
- 예: `velog.io-20260209143022.md`

**파일명 규칙**:
- 특수문자 제거: `/`, `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`
- 공백은 `-`로 변환
- 소문자 사용
- 최대 100자로 제한

**중복 처리**:
- 동일한 파일명이 이미 존재하는 경우
- 자동으로 타임스탬프 suffix 추가: `article-title-20260209143022.md`
- 사용자 확인 없이 새 파일로 저장

### 5. 파일 저장

각 요약을 Obsidian vault의 지정된 경로에 저장합니다.

**저장 경로**: `/Users/choiyoungjun/Documents/Obsidian Vault/articles/2026`

**파일 형식**:
```yaml
---
date: 2026-02-09
source: nytimes.com
url: https://...
title: "문서 제목"
tags:
  - ai
  - machine-learning
  - claude
type: web-article
created_by: articles-summarizer
---

# 문서 제목

## 요약

### 핵심 내용 1
- 상세 설명 1
- 상세 설명 2
- 상세 설명 3

### 핵심 내용 2
- 상세 설명 1
- 상세 설명 2

## 주요 코드 예제
(기술 문서인 경우에만 포함)

```javascript
// 코드 예제와 간단한 설명
```

## 원문 링크
[원문 보기](https://...)
```

**Frontmatter 필드**:
- `date`: 요약 생성 날짜 (YYYY-MM-DD)
- `source`: 도메인 추출 (예: nytimes.com, github.com)
- `url`: 원본 URL
- `title`: 추출된 문서 제목
- `tags`: 내용 기반 자동 추출된 태그 배열 (3-7개)
- `type`: `web-article`, `github-pr`, `github-issue` 중 하나
- `created_by`: 항상 `articles-summarizer`

### 6. 결과 리포트

모든 처리가 완료되면 터미널에 결과를 출력합니다:

```
✅ 요약 완료 (3/5)

성공:
  1. nytimes-ai-breakthrough-2026.md
  2. techcrunch-startup-funding.md
  3. github-pr-anthropics-claude-1234.md

실패:
  1. https://broken-link.com/article (접근 불가)
  2. https://timeout.com/page (타임아웃)
```

## Edge Cases

### 매우 짧은 문서 (< 100 단어)
- 요약 대신 전체 내용 포함
- frontmatter에 `type: short-content` 추가

### 매우 긴 문서 (> 50,000자)
- WebFetch 제한으로 일부 내용이 잘릴 수 있음
- 사용자에게 경고: "일부 내용이 생략될 수 있습니다"
- 가능한 한 주요 내용 위주로 요약

### GitHub API Rate Limit
- 사용자에게 즉시 알림
- 남은 GitHub 링크는 일반 WebFetch로 시도

### 파일 저장 실패
- 에러 메시지 출력
- 해당 요약 내용을 터미널에 출력 (백업)
- 다른 파일은 정상 저장 진행

## Resources

### scripts/process_links.py
링크 처리, 배치 관리, 재시도 로직을 담당하는 Python 스크립트입니다.

**주요 기능**:
- 링크 파싱 및 검증
- 타입별 분류 (일반 URL vs GitHub)
- 배치 처리 로직 (5개씩 그룹화)
- 재시도 메커니즘 (1회, 5초 대기)
- 실패 리포트 생성

**실행 방법**:
```bash
python3 scripts/process_links.py <links-file>
```

### assets/template.md
Obsidian 파일 생성 시 사용할 템플릿입니다.

**포함 내용**:
- YAML frontmatter 구조
- 요약 섹션 템플릿
- 원문 링크 섹션

## Examples

**사용자 입력**:
```
이 링크들 요약해줘:
https://nytimes.com/ai-breakthrough
https://github.com/anthropics/claude/pull/1234
https://techcrunch.com/startup-news
```

**처리 과정**:
1. 3개 링크 검증 완료
2. 병렬로 콘텐츠 가져오기 (5개 이하)
3. 각 문서 순차적으로 요약 생성
4. 파일명: `nytimes-ai-breakthrough.md`, `github-pr-anthropics-claude-1234.md`, `techcrunch-startup-news.md`
5. Obsidian vault에 저장
6. 성공 리포트 출력

## Notes

- 이 스킬은 하루 1-2회, 5개 이하의 링크를 처리하는 것을 기준으로 최적화되어 있습니다
- Python 표준 라이브러리만 사용하므로 외부 의존성이 없습니다
- Obsidian vault 경로는 사용자 환경에 맞게 조정 가능합니다
- 요약 언어는 항상 한국어로 고정됩니다

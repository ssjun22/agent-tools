---
name: confluence-project-qa
description: Confluence 스페이스의 여러 페이지를 교차 참조해야 답할 수 있는 프로젝트 QA·히스토리·회의록·결정 근거 질의, 또는 코딩 에이전트에게 넘길 컨텍스트 팩 추출에 사용. "OI-04 상태 어때?", "REQ-AI-003 구현 스펙", "우리팀 챙겨야 할 미결 이슈", "고쳐쓰기 정책 근거/결정 이유", "주간회의에서 뭐 결정됐지?", "외부 시스템 Y 변경사항 우리팀 영향", "AI 엔진 관련 자료 모아줘", "이 프로젝트에서 X 관련 최근 논의" 등에 발동. 단일 Jira 이슈 조회·코드 질문·단순 파일 검색·Confluence 쓰기 요청에는 발동하지 않음. 매번 스페이스 전체를 풀 스캔하며, 쓰기는 절대 하지 않고, 문서에 없는 내용은 "문서에 없음"으로 답한다.
---

# Confluence Project QA

프로젝트 담당자(PL 등)가 Confluence 스페이스의 여러 문서를 일일이 읽지 않고도 필요한 정보를 얻을 수 있게 하는 스킬. 매번 스페이스 전체를 풀 스캔하고 필터링해서 질문에 답하거나 컨텍스트 팩을 뽑는다.

## When to trigger

- 프로젝트 배경·현황·결정·미결 이슈 질문
- 특정 REQ/OI ID 언급 (`OI-04`, `REQ-AI-003` 등)
- 결정 근거·히스토리 질문 ("왜 이렇게 결정됐어?", "정책 근거가 뭐야?")
- 회의록 결과 질문 ("주간회의에서 뭐 결정됐지?")
- 외부 시스템 변경 영향 ("Y 변경사항 우리팀 영향 뭐야?")
- "우리팀 관련", "AI R&D 관점" 같은 팀 필터 요청
- "컨텍스트 팩", "자료 모아줘", "정리해줘" 같은 컨텍스트 추출 요청
- 여러 회의록·문서를 교차 참조해야 답할 수 있는 질문

## When NOT to trigger

- 단일 Jira 이슈 조회 → `jira` 스킬 사용
- 코드 관련 질문 (Confluence에 답 없음)
- 단순 파일 검색
- Confluence 수정/작성 요청 (이 스킬은 읽기 전용)

## 핵심 원칙 (절대 양보 금지)

1. **환각 금지** — 문서에 없는 내용은 추측·생성하지 않는다. 없으면 "문서에 없음"으로 명시
2. **출처 필수** — 모든 답변에 근거 `page_id` + 원문 발췌 한 줄 표시
3. **읽기 전용** — GET 엔드포인트만 사용. POST/PUT/DELETE 절대 호출 금지
4. **매번 풀 스캔** — 이전 세션 캐시·메모리에 의존하지 않음. 항상 신선한 fetch
5. **팀 관점 필터** — `team-scope.yaml` 기준으로 무관한 내용 제외

## 역할 분리

| 주체 | 역할 |
|---|---|
| **Main Claude (당신)** | 스킬 발동, 모드 판정, Sub-Agent 호출, 받은 정제 컨텍스트로 답변 작성 |
| **Sub-Agent** | Confluence 풀 스캔, 필터링, 정제된 JSON 반환 (답변 문장 생성 금지) |

## Workflow

### Step 1: 설정 존재 확인

`~/.claude/confluence-project-qa/team-scope.yaml` 존재 확인. 없으면:
```
team-scope.yaml이 없습니다. 
~/.claude/confluence-project-qa/team-scope.yaml 에 팀 설정을 작성해주세요.
(예시는 SKILL.md의 team-scope 섹션 참조)
```

### Step 2: 모드 판정

| 입력 패턴 | 모드 |
|---|---|
| 짧은 답 기대 질문 ("X 상태는?", "누가 담당?") | **QA 모드** |
| "모아줘", "컨텍스트 팩", "정리해서", "자료 뽑아줘", "코딩 에이전트에 넘길" | **컨텍스트 팩 모드** |

애매하면 QA 모드 기본값 + 답변 끝에 "컨텍스트 팩으로 만들까요?" 제안.

### Step 3: Sub-Agent 호출

아래 "Sub-Agent Prompt Template"을 `Agent` 도구로 호출:
- `subagent_type`: `general-purpose`
- `description`: "Confluence source 수집"
- `prompt`: 템플릿에서 `{{user_question}}`만 치환. **team-scope.yaml은 경로로 전달**, Sub가 직접 Read (YAML 치환 실수 방지)

### Step 4: 결과 처리 및 답변

Sub-Agent가 반환하는 JSON:
```json
{
  "question_intent": ["현재 상태 질의"],
  "total_pages_scanned": 52,
  "included_pages": [
    {"page_id": "...", "title": "...", "relevance": "high", "key_excerpts": "..."}
  ],
  "excluded_pages": [
    {"page_id": "...", "title": "...", "reason": "..."}
  ],
  "excluded_count": 42,
  "notes": "..."
}
```

**QA 모드 답변 포맷**:

```markdown
## 답변 (TL;DR)
[문서 기반 핵심 3줄 이내]

## 상세 (필요 시)
...

## 출처
- page_id=`XXX` [제목]
  - 근거: "원문 발췌 한 줄" (key_excerpts에서 추출)
- page_id=`YYY` [제목]
  - 근거: "..."
```

**컨텍스트 팩 모드**: `/tmp/context-pack-{topic-slug}-{YYYYMMDD-HHMMSS}.md` 파일 저장. 아래 "컨텍스트 팩 포맷" 섹션 참조.

## Sub-Agent Prompt Template

아래 전체를 `Agent` 도구의 `prompt`로 전달. 치환 변수는 `{{user_question}}` 하나뿐.

````
# 역할
당신은 Atlassian Confluence를 매번 풀 스캔하여 정제된 컨텍스트를 반환하는 source 수집 전담 에이전트입니다. **답변 작성은 하지 않습니다.** 필터링된 페이지의 본문 발췌만 JSON으로 반환합니다.

# 원칙 (절대 양보 금지)
1. 문서에 없는 내용을 추측·생성하지 말 것
2. 쓰기 API (POST/PUT/DELETE) 호출 절대 금지. GET만 사용
3. 반환 데이터에 추측·유추·일반 지식 포함 금지
4. 답변 문장 생성 금지 — JSON만 출력

# 사용 도구 (엄격)
- **반드시 `Bash` + `curl` 사용**. `WebFetch`는 Basic auth 헤더 미지원이므로 쓰지 말 것
- 설정 파일 읽기는 `Read`
- 파싱·병렬 실행은 bash 또는 Python

# 환경 로드

**Step 0-1. Credential 로드**:
```bash
source /Users/choiyoungjun/agent-tools/env.local
# → $JIRA_EMAIL, $JIRA_API_TOKEN 사용 가능
```

**Step 0-2. team-scope 설정 읽기** (`Read` 도구 사용):
- 경로: `/Users/choiyoungjun/.claude/confluence-project-qa/team-scope.yaml`
- 추출할 값:
  - `space.id` (문자열)
  - `space.base_url` (문자열, 예: `https://daekyo.atlassian.net/wiki`)
  - `team.ownership` (리스트)
  - `team.interest` (리스트)
  - `team.keywords` (리스트)

# 사용자 질문

{{user_question}}

# 엔드포인트 (모두 GET)

아래 `BASE_URL`은 team-scope의 `space.base_url`로, `SPACE_ID`는 `space.id`로 치환하여 사용. `<PAGE_ID>`는 목록에서 받은 실제 id로 런타임 치환.

**페이지 목록** (페이지네이션: `_links.next` 따라감, **archived 제외**):
```
GET {BASE_URL}/api/v2/spaces/{SPACE_ID}/pages?limit=100&status=current
```
- `status=current` 쿼리 파라미터로 archived/trashed/deleted를 서버단에서 제외
- v2 API 기본값이 `current,archived`이므로 **반드시 명시**해야 함

**페이지 본문** (응답의 `status` 필드 함께 확인):
```
GET {BASE_URL}/api/v2/pages/<PAGE_ID>?body-format=storage
```
- 응답 JSON의 `status` 값이 `current`가 아니면 (archived/trashed/deleted/draft) 파싱하지 말고 즉시 skip — 이중 방어선

인증: `curl -u "$JIRA_EMAIL:$JIRA_API_TOKEN" -s <URL>`

# 작업 순서

## Step ① 질문 의도 파악

사용자 질문을 아래 4가지 중 **해당되는 것 모두** 선택 (복수 가능, 배열로 기록):
- **현재 상태 질의**: "지금", "최신", "현재", "구현 요건", "스펙" 키워드. 구버전 제외 가능
- **히스토리 질의**: "왜", "어떻게 바뀌어왔나", "근거", "결정 이유" 키워드. 구버전·초기 토론 포함
- **회의록 질의**: 특정 회의 결과 또는 "회의" 키워드. 최신 회의록 우선
- **팀 관점 필터 질의**: "우리팀", "AI R&D" 등. team-scope 필터 강하게 적용

**복합 인텐트 규칙**:
- "현재 상태" + "히스토리" 동시 → **히스토리 필터 우선** (구버전도 포함)
- "회의록" + "팀 관점" → 팀 필터 적용 후 최신 회의록 우선

## Step ② 풀 스캔

- concurrency 10으로 전체 페이지 본문 병렬 fetch (`xargs -P 10` 또는 Python asyncio)
- HTTP 000/5xx 에러 시 최대 2회 재시도 (지수 백오프: 1s, 2s)
- body-format=storage로 받은 뒤 plain text 변환:
  - HTML 태그 제거
  - 표는 `|` 구분자로 유지
  - 공백 정규화

## Step ③ 관련성 평가 + 필터링

각 페이지를 아래 규칙으로 분류:

### 제외 기준 (excluded)
1. **archived 상태** — 페이지 응답의 `status` 필드가 `current`가 아닌 모든 페이지 (archived/trashed/deleted/draft). **질문 의도와 무관하게 항상 제외**. `excluded_pages`에도 사유 `"status=archived"` 등으로 표기
2. **질문 주제와 무관** — 질문 키워드·의도와 매칭 없음
3. **팀 관점 무관** — team-scope의 `ownership` / `interest` / `keywords` 중 어느 것과도 매칭 없음 (우리팀이 몰라도 되는 내용)
4. **구버전/초기 토론 + 순수 "현재 상태" 질의** — 제목에 `v1.0`, `v2.0` 등 구버전 표기 + 같은 주제의 상위 버전 존재 + `question_intent`에 "히스토리" **없음**
5. **확정 전 토론 + 순수 "현재 상태" 질의** — "킥오프", "검토 중", "논의 필요" 포함 + 더 최신 의사결정 페이지 존재 + `question_intent`에 "히스토리" **없음**

### 중복 콘텐츠 처리 (latest-wins)

여러 페이지가 **같은 주제·같은 사실**을 다루어 내용이 겹칠 때, 충돌하든 단순 중복이든 **최신 문서를 단일 근거(source of truth)로 채택**하고 구 문서는 보조 자료 이하로 강등.

**중복 판정 신호** (둘 이상 일치 시 중복으로 간주):
- 동일 REQ/OI ID (`REQ-AI-003`, `OI-04` 등)를 양쪽이 정의/언급
- 동일 정책·결정 사항을 양쪽이 명시 (예: "수행평가 점수 저장 방식")
- 회의록 vs 정의서처럼 같은 결정이 양쪽에 적힘
- key_excerpts 후보 문장이 사실상 동일 의미

**최신 판정 순서** (위에서부터 적용, 첫 번째로 해석되는 신호 채택):
1. `[의사결정 완료]` 접두사가 붙은 페이지 > 안 붙은 페이지
2. 제목의 버전 번호: `v2.2` > `v2.0` > `v1.0`
3. 제목의 날짜 접두사 `[YYMMDD]` / `[YYYYMMDD]` 중 더 큰 날짜
4. v2 API 응답의 `version.createdAt` (또는 `lastModified`) 더 최근값
5. tie-breaker: **page_id 더 큰 값** (Confluence는 새 페이지일수록 큰 id)

**충돌 처리**:
- 최신 문서를 **high**로, 구 문서는 **excluded** 또는 **mid**로 강등
- `question_intent`에 "히스토리"가 있으면: 구 문서도 **mid**로 살리되 `key_excerpts`에 "(구버전, v2.2로 대체됨)" 같은 메타 정보를 **원문 발췌에 덧붙이지 말고** `excluded_pages.reason`에만 기록
- 동일 사실에 대해 최신·구버전이 **상충**하면 최신만 인용하고 `notes`에 "버전 X와 Y 간 상충, X 채택 (최신)" 명시

### 우선 인용 (priority boost)
- 제목에 `[의사결정 완료]` 접두사 → **권위 있는 결론**으로 최우선 인용
- 제목에 날짜 접두사 `[YYMMDD]` 또는 `[YYYYMMDD]` 회의록 → 가장 최근 날짜 우선
  - 동일 날짜 복수 tie-breaker: **page_id 가장 큰 값** (최신 생성) 우선
  - 2자리/8자리 연도 혼재 시 2자리 기본 해석, 안 맞으면 8자리

### 분류 결과
- **high**: 답변에 반드시 포함할 핵심 근거
- **mid**: 보조 근거
- **excluded**: 반환 JSON의 `excluded_pages`에 **상위 10건**만 사유 포함 (디버깅용)

## Step ④ JSON 반환

**답변을 작성하지 말고**, 아래 포맷 그대로 출력:

```json
{
  "question_intent": ["현재 상태 질의"],
  "total_pages_scanned": 52,
  "included_pages": [
    {
      "page_id": "2654210873",
      "title": "[수행평가] 개발요건 정의서 v2.2",
      "relevance": "high",
      "key_excerpts": "REQ_STU_03 | 과제 제출 (OCR) | 손글씨 사진 촬영 → OCR 변환 → 텍스트 저장. 입력 제한: 제목 50자 / 본문 10,000자. 시스템: 수행평가 제품, 우선순위: 상, 연동: OCR 엔진"
    }
  ],
  "excluded_pages": [
    {
      "page_id": "2654634718",
      "title": "[수행평가] 요구사항정의서 v2.0 (참고)",
      "reason": "구버전 (v2.2 존재) + 순수 현재 상태 질의"
    }
  ],
  "excluded_count": 42,
  "notes": "구버전 2개, 팀 관점 무관 28개, 초기 토론 2개 제외"
}
```

**`key_excerpts` 규칙**:
- 해당 페이지에서 질문과 직접 관련된 부분의 **원문 발췌 그대로** (문단 단위)
- 요약·해석·생성 금지
- Main Claude가 "근거 문장"으로 재인용할 수 있어야 함

## 보고
JSON 객체만 출력하고 종료. 별도의 자연어 답변 텍스트 생성 금지.
````

## 컨텍스트 팩 포맷

파일 경로: `/tmp/context-pack-{topic-slug}-{YYYYMMDD-HHMMSS}.md`

```markdown
# 컨텍스트 팩: {주제}

**생성 시각**: {timestamp}
**소스**: Confluence (space_id: {space.id})
**질문 의도**: {question_intent 배열}
**포함 페이지**: {N}개 (전체 {M}개 중)

---

## {페이지 제목 1}
**page_id**: {id}
**relevance**: high|mid

{key_excerpts}

---

## 주의
- 본 파일은 Confluence 특정 시점 발췌입니다. 최신 상태는 원본 참조
- 문서에 없는 내용은 포함되지 않습니다 (환각 방지)
```

Main Claude가 사용자에게는 파일 경로 + 간단 요약만 표시:
```
컨텍스트 팩 저장: /tmp/context-pack-ai-engine-20260422-153012.md

포함: N개 페이지 (주요 출처: ~~~)
→ 이 파일을 다음 에이전트 프롬프트에 첨부하세요.
```

## team-scope.yaml 예시

`~/.claude/confluence-project-qa/team-scope.yaml`:

```yaml
space:
  id: "2550300994"
  name: "SKD2"
  base_url: "https://daekyo.atlassian.net/wiki"

team:
  name: AI R&D

  ownership:
    - AI 평가 엔진
    - OCR 엔진
    - 자체 CMS
    - 수행평가 전용 LMS
    - 제품 FE/BE

  interest:
    - 마케팅 일정
    - 콘텐츠 준비 상태
    - SSO·알림톡 연동 스펙

  keywords:
    - AI R&D
    - REQ-AI-
    - REQ-STU-
    - REQ-TCH-
    - REQ-CON-
    - 루브릭
    - 성취기준
    - KReaD
```

## NEVER

- **NEVER 추측으로 답변** — 문서에 없으면 "문서에 없음"
- **NEVER 쓰기 API 호출**
- **NEVER 이전 세션 기억·캐시 재사용**
- **NEVER team-scope.yaml 수정** — 에이전트는 읽기만
- **NEVER 단일 페이지만 읽고 답변** — 풀 스캔 원칙
- **NEVER Sub-Agent가 답변 문장 생성** — Sub는 발췌(key_excerpts)만
- **NEVER 외부 지식으로 빈칸 채우기** — "추측"이 아닌 "발췌"
- **NEVER WebFetch로 인증 API 호출** — auth 헤더 미지원
- **NEVER archived 페이지 인용** — `status != current`이면 본문도 읽지 않음
- **NEVER 구버전과 최신본을 동등하게 인용** — 중복 시 최신 채택, 구버전은 강등/제외

## Safety

- 읽기 전용: Confluence 쓰기 API 절대 호출 안 함
- team-scope.yaml은 사용자 수동 편집 대상. 에이전트 자동 수정 금지
- 컨텍스트 팩 파일에 민감 정보 포함 가능성 — 사용자가 검토 필요

## 디버그 모드

사용자가 질문에 `--debug` 플래그 포함 또는 "필터 과정 보여줘" 명시 시:
- Sub-Agent 반환 JSON의 `excluded_pages` 상세 리스트 전체 표시
- `excluded_count`와 `notes` 필드 함께 표시

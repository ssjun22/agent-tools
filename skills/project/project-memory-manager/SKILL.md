---
name: project-memory-manager
description: |
  Manages project context in Obsidian vault with OpenSpec integration for feature specifications.

  Use when the user wants to:
  - Record meeting notes or decisions
  - Add/update business domain knowledge (user, evaluation, lesson domains)
  - Log quick decisions or issue resolutions
  - Track work progress and follow-up tasks
  - Create feature specs (auto-triggers OpenSpec)

  Triggers:
  - "add to project memory"
  - "record this meeting"
  - "update domain knowledge"
  - "[project name] + meeting/decision/work/domain"

  The skill manages three areas:
  - project.md: Central index with references (progressive disclosure)
  - domain/: Business domain folders (user/, evaluation/, lesson/)
  - meetings/: Meeting notes, reviews, and decisions

  OpenSpec Integration:
  - Auto-creates feature specs in code repository
  - Links specs back to project.md with abbreviated paths
  - Executes OpenSpec CLI automatically (optional)
---

# Project Memory Manager

## Overview

이 스킬은 **프로젝트 맥락**과 **비즈니스 도메인**을 Obsidian vault에서 관리하며, OpenSpec과 통합하여 기능 spec을 자동으로 생성합니다.

**핵심 원칙:**
- **점진적 공개 (Progressive Disclosure)**: project.md는 요약만, 상세 내용은 참조
- **물리적 분리**: 맥락(Obsidian) vs 코드/Spec(Repository)
- **자동 통합**: 회의/결정 → OpenSpec 자동 생성

**관리 구조:**

```
Obsidian Vault (맥락 + 비즈니스 도메인)
/path/to/vault/projects/
├── project.md              # 중앙 인덱스
├── domain/                 # 비즈니스 도메인
│   ├── user/               # User 도메인
│   ├── evaluation/         # Evaluation 도메인
│   └── lesson/             # Lesson 도메인
└── meetings/               # 회의록/결정
    ├── 2026-02-09-dev.md
    └── 2026-02-09-meeting.md

Code Repository (기능 spec)
/path/to/repo/
└── openspec/               # OpenSpec (자동 관리)
    ├── changes/
    └── specs/
```

---

## Prerequisites

### 1. 설정 파일 생성

**설정 파일 위치:**
스킬은 다음 순서로 설정 파일을 찾습니다:
1. `{primary_working_dir}/.claude/project-memory-config.yaml` (우선)
2. `~/.claude/project-memory-config.yaml` (fallback)

**권장:** agent-tools 레포지토리에서 관리하는 경우, 레포지토리 루트에 `.claude/` 디렉토리를 만드세요.

```bash
# agent-tools 레포지토리 루트에서 실행
cd /path/to/agent-tools

# 설정 디렉토리 생성
mkdir -p .claude

# 설정 파일 생성
cat > .claude/project-memory-config.yaml << 'EOF'
projects:
  - name: "프로젝트명"
    alias: ["별칭1", "별칭2"]

    # Obsidian vault 경로 (맥락 관리)
    obsidian_path: "/Users/username/Documents/Obsidian Vault/projects"

    # 코드 레포지토리 경로 (OpenSpec)
    repo_path: "/Users/username/code/project-repo"

    # OpenSpec 사용 여부
    use_openspec: true

    # 기본 회의 타입
    default_meeting_types: ["dev", "meeting", "cto-review"]
EOF
```

### 2. 초기 폴더 구조 생성

```bash
# Obsidian vault 구조
cd /path/to/obsidian/vault/projects
mkdir -p domain meetings

# project.md 생성 (템플릿 사용)
cp /path/to/this/skill/assets/project-template.md project.md
```

### 3. OpenSpec 설치 (선택사항)

```bash
npm install -g @fission-ai/openspec@latest

# 레포지토리에서 초기화
cd /path/to/repo
openspec init
```

---

## Workflow

### 사용 방법

```bash
# 기본 사용
/project-memory-manager [내용]

# 예시
/project-memory-manager 오늘 마케팅팀 회의 내용 추가
/project-memory-manager User 도메인 정보 업데이트
/project-memory-manager Redis 캐싱 작업 완료
```

---

### 상황 1: 회의록 추가

**트리거:**
- "오늘 회의 내용 추가"
- "마케팅팀 미팅 기록"
- "CTO 리뷰 결과"

**플로우:**

```
1. 프로젝트 감지
   - 설정 파일 읽기
   - 입력에서 프로젝트 키워드 찾기
   - 없으면 사용자에게 질문

2. 회의 정보 수집
   Q: "회의 유형을 선택해주세요:"
      1) dev (개발팀 회의)
      2) meeting (일반 회의/유관부서) - 추천
      3) cto-review (CTO/상위자 리뷰)
      4) 기타 (직접 입력)

3. 날짜 확인
   Q: "회의 날짜는?" (기본: 오늘 날짜)

4. 파일 생성
   경로: {obsidian_path}/meetings/{YYYY-MM-DD}-{type}.md
   템플릿 사용

5. 내용 입력
   사용자 제공 내용을 템플릿 형식으로 포맷팅

6. OpenSpec 제안 (use_openspec: true인 경우)
   Q: "회의에서 새로운 기능이 결정되었나요?"

   → Yes 선택 시:
     Q: "기능 이름은?" (예: add-kakao-login)

     Bash 실행:
       cd {repo_path} && openspec new {feature-name}

     성공 시 project.md 업데이트:
       ## 진행 중
       - {기능명} (`{feature-name}`)
         - Spec: /{repo_path_abbrev}/openspec/changes/{feature-name}/
         - 배경: [[meetings/{YYYY-MM-DD}-{type}]]

   → No: 완료

7. 완료 메시지
   "✅ 프로젝트 메모리 업데이트 완료

    📂 회의록: meetings/{YYYY-MM-DD}-{type}.md
    📋 OpenSpec: /{repo_path_abbrev}/openspec/changes/{feature-name}/
    📄 project.md 업데이트됨"
```

**에러 처리:**
- OpenSpec 미설치: 설치 안내 + 수동 실행 가이드
- 레포지토리 경로 없음: 설정 파일 확인 요청
- 파일 이미 존재: 덮어쓰기/취소 선택

---

### 상황 2: 비즈니스 도메인 추가/수정

**트리거:**
- "User 도메인 업데이트"
- "Evaluation 규칙 추가"
- "도메인 지식 정리"

**플로우:**

```
1. 프로젝트 감지

2. 도메인 확인
   Q: "어떤 도메인인가요?"
      - 기존 도메인 목록 표시 (domain/ 아래 폴더)
      - 새 도메인 생성 옵션

   예시:
      1) user
      2) evaluation
      3) lesson
      4) 새 도메인 생성

3. 파일 선택
   선택한 도메인 아래 파일 목록:
   - README.md (도메인 개요)
   - entities.md (엔티티 정의)
   - rules.md (비즈니스 규칙)
   - workflows.md (워크플로우)
   - 새 파일 생성

   Q: "어떤 파일을 수정/생성할까요?"

4. 파일 확인
   - 존재하면: 읽기 → 수정
   - 없으면: 빈 템플릿 생성

5. 내용 추가/수정
   사용자 입력을 해당 섹션에 추가

6. project.md 업데이트 제안
   Q: "project.md에도 반영할까요?"
   → Yes: project.md에 요약 추가
   → No: domain 파일만 수정

7. 관련 회의록 연결 제안
   Q: "이 변경의 배경이 된 회의가 있나요?"
   → Yes: meetings/ 파일 참조 추가
   → No: 완료

8. 완료 메시지
   "✅ 도메인 지식 업데이트 완료

    📂 파일: domain/{domain}/{file}.md
    📄 project.md: 업데이트됨"
```

---

### 상황 3: 빠른 결정/이슈 해결

**트리거:**
- "STT 응답 시간 문제로 멀티모달로 변경"
- "Redis 대신 in-memory 캐시 사용 결정"
- "버그 해결: 로그인 세션 타임아웃"

**플로우:**

```
1. 프로젝트 감지

2. 결정 사항 분석
   - 문제 파악
   - 해결책 파악

3. 기록 위치 확인
   Q: "어떻게 기록할까요?"
      1) 간단 기록 - project.md에만 추가
      2) 상세 기록 - meetings/에 decision 파일 생성
      3) 둘 다 (추천)

4. project.md 업데이트
   ## 주요 결정 사항
   - **[{날짜}] {제목}**
     - 문제: {문제 설명}
     - 결정: {해결책}
     - 상세: [[meetings/{날짜}-decision]]

5. meetings/ 파일 생성 (상세 기록 선택 시)
   경로: {obsidian_path}/meetings/{날짜}-decision.md

   내용:
   - 문제 상황
   - 결정 내용
   - 이유/배경
   - 영향 범위

6. 도메인 업데이트 제안
   Q: "이 결정이 비즈니스 도메인에 영향을 주나요?"
   → Yes: domain/{domain}/ 업데이트 제안

7. OpenSpec 제안
   Q: "이 변경을 OpenSpec으로 관리할까요?"
   → Yes: openspec new {change-name} 실행

8. 완료 메시지
```

---

### 상황 4: 작업 진행/완료 + 후속

**트리거:**
- "Redis 캐싱 작업 완료"
- "API 응답 시간 개선 50% 진행 중"
- "로그인 버그 해결"

**플로우:**

```
1. 프로젝트 감지

2. 작업 상태 확인
   Q: "작업 상태가 어떻게 되나요?"
      1) 완료 (100%)
      2) 진행 중 (%)
      3) 블로킹됨

3. project.md 업데이트
   ## 최근 완료 (완료된 경우)
   - [x] {작업명} ({날짜} 완료)

   또는

   ## 진행 중
   - [ ] {작업명} ({진행률}%)

4. 후속 작업 확인 ⭐ 중요!
   Q: "이 작업과 관련된 후속 작업이 있나요?"

   사용자 입력 받기

   project.md 업데이트:
   ## 다음 작업
   - [ ] {후속 작업 1}
   - [ ] {후속 작업 2}

5. 도메인 업데이트 제안
   Q: "이 작업으로 비즈니스 도메인 변경이 있나요?"
   → Yes: domain/ 업데이트

6. 관련 회의/리뷰 기록 제안
   Q: "관련 리뷰나 회의를 기록할까요?"
   → Yes: meetings/ 파일 생성

7. 완료 메시지
   "✅ 작업 상태 업데이트 완료

    📋 {상태}: {작업명}
    📝 후속 작업: {개수}개 추가됨"
```

---

## Configuration

### 설정 파일: project-memory-config.yaml

**위치 우선순위:**
1. `{primary_working_dir}/.claude/project-memory-config.yaml`
2. `~/.claude/project-memory-config.yaml`

**예시:**

```yaml
projects:
  # 프로젝트 1
  - name: "톡톡 평가"
    alias: ["talktalk", "톡톡", "talktalk-eval"]

    # Obsidian vault 경로 (맥락 + 도메인)
    obsidian_path: "/Users/choiyoungjun/Documents/Obsidian Vault/daekyo/projects"

    # 코드 레포지토리 경로 (OpenSpec)
    repo_path: "/Users/choiyoungjun/knowre/talktalk-eval"

    # OpenSpec 사용 여부
    use_openspec: true

    # 기본 회의 타입
    default_meeting_types: ["dev", "meeting", "cto-review"]

  # 프로젝트 2 (예시)
  - name: "다른 프로젝트"
    alias: ["project2"]
    obsidian_path: "/path/to/vault/project2"
    repo_path: "/path/to/repo2"
    use_openspec: false
```

### 경로 축약 규칙

project.md에서 OpenSpec 파일 참조 시:

```markdown
# 절대 경로 (실제)
/Users/choiyoungjun/knowre/talktalk-eval/openspec/changes/add-kakao-login/

# 축약 경로 (표시)
/knowre/talktalk-eval/openspec/changes/add-kakao-login/
```

스킬은 설정 파일의 `repo_path`를 참조하여 전체 경로를 재구성합니다.

---

## Templates

### assets/project-template.md

템플릿 파일 위치: `skills/project/project-memory-manager/assets/project-template.md`

```markdown
# {프로젝트명}

> 마지막 업데이트: {날짜}

## 📋 프로젝트 개요

{프로젝트 설명}

**목표:** {주요 목표}
**현재 단계:** {단계 설명}

---

## 🎯 주요 결정 사항

최신순으로 나열

- **[YYYY-MM-DD] {제목}**
  - 결정: {결정 내용}
  - 이유: {이유}
  - 상세: [[meetings/YYYY-MM-DD-type]]

---

## 🚧 진행 중인 작업

- {작업명} (`{openspec-id}`)
  - Spec: /{repo_abbrev}/openspec/changes/{id}/
  - 배경: [[meetings/YYYY-MM-DD-type]]
  - 진행률: XX%

---

## ✅ 최근 완료

- [x] {작업명} (YYYY-MM-DD 완료)

---

## 📝 다음 작업

- [ ] {후속 작업 1}
- [ ] {후속 작업 2}

---

## 🔗 주요 링크

- 비즈니스 도메인: [[domain/user]], [[domain/evaluation]]
- 최근 회의: [[meetings/YYYY-MM-DD-meeting]]
- OpenSpec: /{repo_abbrev}/openspec/
```

### assets/meetings-template.md

```markdown
# {회의 제목}

**날짜:** {YYYY-MM-DD}
**유형:** {dev/meeting/cto-review}
**참석자:** {참석자 목록}

---

## 안건

1. {안건 1}
2. {안건 2}

---

## 논의 내용

### {주제 1}

{논의 내용}

---

## 결정 사항

- **{결정 1}**
  - 이유: {이유}
  - 담당: {담당자}
  - 기한: {날짜}

---

## 액션 아이템

- [ ] {작업 1} - {담당자} - {기한}
- [ ] {작업 2} - {담당자} - {기한}

---

## 참고

- 관련 도메인: [[domain/{domain}]]
- OpenSpec: (있다면 링크)
```

### assets/domain-template.md

```markdown
# {도메인명} Domain

> 마지막 업데이트: {날짜}

## 개요

{도메인 설명}

---

## 주요 엔티티

### {Entity 1}

**속성:**
- {속성 1}: {타입} - {설명}
- {속성 2}: {타입} - {설명}

**관계:**
- {다른 엔티티와의 관계}

---

## 비즈니스 규칙

- {규칙 1}
- {규칙 2}

---

## 주요 워크플로우

### {워크플로우 1}

1. {단계 1}
2. {단계 2}

---

## 변경 이력

- **[YYYY-MM-DD]** {변경 내용}
  - 배경: [[meetings/YYYY-MM-DD-type]]
```

---

## Error Handling

### OpenSpec 자동 실행 실패

**에러 1: OpenSpec 미설치**

```
⚠️ OpenSpec이 설치되지 않았습니다.

설치 방법:
  npm install -g @fission-ai/openspec@latest

또는 수동으로 실행:
  cd {repo_path}
  /opsx:new {feature-name}

meetings/ 파일은 생성되었습니다.
```

**에러 2: 레포지토리 경로 없음**

```
⚠️ 레포지토리 경로를 찾을 수 없습니다: {repo_path}

설정 파일을 확인해주세요:
  {working_dir}/.claude/project-memory-config.yaml
  또는
  ~/.claude/project-memory-config.yaml

repo_path가 올바른지 확인하세요.
```

**에러 3: OpenSpec 실행 오류**

```
⚠️ OpenSpec 실행 중 오류:
{error_message}

수동 실행:
  cd {repo_path}
  /opsx:new {feature-name}

meetings/ 및 project.md는 업데이트되었습니다.
```

### 파일 충돌

**이미 존재하는 파일**

```
⚠️ 파일이 이미 존재합니다:
meetings/{날짜}-{type}.md

어떻게 할까요?
1) 덮어쓰기
2) 내용 추가 (append)
3) 취소
```

### 프로젝트 감지 실패

```
⚠️ 프로젝트를 감지할 수 없습니다.

입력에서 프로젝트 키워드를 찾지 못했습니다.
설정 파일의 프로젝트 목록:

1) 톡톡 평가 (talktalk, 톡톡, talktalk-eval)
2) 다른 프로젝트 (project2)

어느 프로젝트인가요?
```

---

## OpenSpec Integration

### 통합 방식

project-memory-manager는 OpenSpec과 **느슨하게 결합**되어 있습니다:

- OpenSpec 없어도 동작 가능 (use_openspec: false)
- OpenSpec 명령어를 Bash로 자동 실행
- 실패 시 수동 실행 가이드 제공
- project.md에서 축약 경로로 참조

### OpenSpec 워크플로우

```
회의/결정 → meetings/ 생성
           ↓
    OpenSpec 제안
           ↓
      사용자 승인
           ↓
  Bash: openspec new {name}
           ↓
  openspec/changes/{name}/ 생성
           ↓
  project.md에 링크 추가
```

### 경로 참조 방식

**설정:**
```yaml
repo_path: "/Users/choiyoungjun/knowre/talktalk-eval"
```

**project.md:**
```markdown
Spec: /knowre/talktalk-eval/openspec/changes/add-kakao-login/
```

**실제 파일 접근 시:**
스킬이 설정의 `repo_path`를 참조하여 전체 경로 재구성:
```
/Users/choiyoungjun/knowre/talktalk-eval/openspec/changes/add-kakao-login/
```

---

## Best Practices

### 1. Progressive Disclosure

project.md는 요약만 담고, 상세는 참조로:

```markdown
✅ Good:
## 주요 결정
- API 변경 결정 → [[meetings/2026-02-09-decision]]

❌ Bad:
## 주요 결정
- API 변경 결정
  - 문제: ...
  - 해결: ...
  - 이유: ...
  (너무 상세함)
```

### 2. 비즈니스 도메인 관리

domain/은 서비스 핵심 개념만:

```
✅ domain/user/       # User 도메인
✅ domain/evaluation/ # Evaluation 도메인

❌ domain/tech-stack.md    # 기술 정보 (meetings/에서 관리)
❌ domain/architecture.md  # 아키텍처 (meetings/에서 관리)
```

### 3. 회의록 활용

기술적 결정도 meetings/에 기록:

```markdown
# meetings/2026-02-09-dev.md

## 결정 사항
- Redis 캐싱 도입
  - 이유: 응답 시간 개선
  - 기술: Redis 6.x
```

### 4. OpenSpec 선택적 사용

모든 변경이 OpenSpec 필요한 것은 아님:

- ✅ 새 기능 추가 → OpenSpec
- ✅ 큰 변경 사항 → OpenSpec
- ❌ 작은 버그 수정 → meetings/만
- ❌ 간단한 개선 → meetings/만

---

## Troubleshooting

### Q: 설정 파일을 어디에 두어야 하나요?

A: 두 가지 옵션이 있습니다:
- **로컬 설정 (권장)**: `{agent-tools}/.claude/project-memory-config.yaml` - 레포지토리별 설정, Git으로 관리 가능
- **전역 설정**: `~/.claude/project-memory-config.yaml` - 모든 프로젝트에서 사용

스킬은 로컬 설정을 우선적으로 찾고, 없으면 전역 설정을 사용합니다.

### Q: OpenSpec 없이도 사용 가능한가요?

A: 네! 설정에서 `use_openspec: false`로 하면 OpenSpec 없이도 완전히 동작합니다.

### Q: 여러 프로젝트를 관리할 수 있나요?

A: 네! 설정 파일에 여러 프로젝트를 추가하면 자동으로 감지합니다.

### Q: 기존 MEMORY.md/DOMAIN.md는 어떻게 하나요?

A: 새로운 구조로 마이그레이션하거나 삭제하세요. 새 구조는 완전히 다릅니다.

### Q: 축약 경로를 못 찾는다면?

A: 설정 파일의 `repo_path`를 확인하세요. 스킬은 이 경로를 기반으로 전체 경로를 재구성합니다.

---

## Migration Guide

### 기존 MEMORY.md → meetings/

```bash
# 기존 MEMORY.md의 각 날짜별 내용을
# meetings/YYYY-MM-DD-dev.md 형식으로 분리

# 예시
## 2026-02-09
**이슈 해결: API 개선**
- ...

→ meetings/2026-02-09-dev.md
```

### 기존 DOMAIN.md → domain/

```bash
# 기존 DOMAIN.md의 기술 스택, 아키텍처 등은
# meetings/에서 관리하거나 나중에 별도 구조 추가

# 비즈니스 도메인 관련 내용만
# domain/{도메인명}/ 으로 이동
```

---

## Resources

### 관련 스킬

- **skill-creator**: 새 스킬 생성/수정
- **weekly-scrum-summarizer**: 주간 스크럼 요약 (meetings/ 참조 가능)

### 외부 도구

- **OpenSpec**: https://openspec.dev/
- **Obsidian**: https://obsidian.md/

### 설정 파일

- `{working_dir}/.claude/project-memory-config.yaml`: 프로젝트 설정 (우선)
- `~/.claude/project-memory-config.yaml`: 전역 설정 (fallback)
- `assets/`: 템플릿 파일들

# Handoff Hooks Installation Guide

이 문서는 handoff 전략의 hooks를 설치하는 방법을 설명합니다.

## Available Hooks

handoff 전략은 세 가지 Claude Code hook을 제공합니다:

1. **session-start**: 세션 시작 시 자동으로 최신 handoff 로드
2. **session-end**: 세션 종료 시 자동으로 handoff 업데이트
3. **pre-compact**: 컨텍스트 압축 전 자동으로 handoff 업데이트

## Installation

### 1. Prepare Hook Directory

프로젝트의 `.claude/hooks` 디렉토리를 생성합니다:

```bash
mkdir -p .claude/hooks
```

### 2. Copy Hook Scripts

handoff-strategy의 hooks를 프로젝트로 복사합니다:

```bash
# 전체 복사 (권장)
cp -r agent-tools/skills/shared/agent-strategy-manager/strategies/handoff-strategy/hooks/* .claude/hooks/

# 또는 개별 복사
cp agent-tools/.../hooks/session-start .claude/hooks/
cp agent-tools/.../hooks/session-end .claude/hooks/
cp agent-tools/.../hooks/pre-compact .claude/hooks/
```

### 3. Make Hooks Executable

```bash
chmod +x .claude/hooks/session-start
chmod +x .claude/hooks/session-end
chmod +x .claude/hooks/pre-compact
```

### 4. Configure Claude Code Hooks

**Option A: 제공된 settings.json 복사** (권장)

```bash
cp agent-tools/.../hooks/settings.json .claude/settings.local.json
```

**Option B: 수동으로 `.claude/settings.local.json` 작성**

```json
{
  "hooks": {
    "sessionStart": "bash .claude/hooks/session-start",
    "sessionEnd": "bash .claude/hooks/session-end",
    "preCompact": "bash .claude/hooks/pre-compact"
  }
}
```

**참고**: `settings.local.json`은 Git에 커밋되지 않으므로 팀원마다 개별 설정이 필요합니다.

### 5. Initialize Handoff Directory

handoff 디렉토리와 index 파일을 초기화합니다:

```bash
mkdir -p .claude/handoffs
cp agent-tools/.../assets/index-template.md .claude/handoffs/index.md
```

## Hook Details

### session-start

**Trigger**: Claude Code 세션 시작 시

**Action**:
1. `.claude/handoffs/index.md` 존재 확인
2. 가장 최근 handoff 파일 찾기
3. AI에게 handoff 읽기 및 요약 지시

**Output** (AI가 실행):
```
[Handoff 로드됨]

이전 세션 컨텍스트:
- 작업: Auth Refactor
- 진행률: 60%
- 마지막 작업: JWT 토큰 검증 로직 구현
- 다음 단계: 리프레시 토큰 구현

어떤 작업을 이어가시겠습니까?
```

### session-end

**Trigger**: Claude Code 세션 종료 시

**Action**:
1. AI에게 handoff 업데이트 지시
2. 현재 세션의 작업 내용 기록
3. index.md 업데이트

**Output** (AI가 실행):
```
Handoff updated for next session
```

### pre-compact

**Trigger**: Claude Code 컨텍스트 압축 전

**Action**:
1. handoff 디렉토리 존재 확인
2. AI에게 handoff 업데이트 지시
3. 현재 세션 작업 내용 저장

**Output**:
```
=== Context Compaction: Updating Handoff ===

🤖 AI Agent Instructions:
Context is about to be compacted. Save important information to handoff NOW:
  1. Update handoff file with current session's work
  2. Update index.md
  3. Keep under ~2000 tokens

Handoff updated before compaction.
```

## Verification

hooks가 올바르게 설치되었는지 확인:

### Test session-start

```bash
bash .claude/hooks/session-start
```

예상 출력: handoff 로드 메시지 또는 "No handoff files found"

### Test session-end

```bash
bash .claude/hooks/session-end
```

예상 출력: AI에게 handoff 업데이트 지시 메시지

### Test pre-compact

preCompact hook은 Claude Code 내부에서 자동으로 트리거되므로 수동 테스트가 어렵습니다.

대신 동작 확인:
```bash
# Hook 파일 확인
cat .claude/hooks/pre-compact

# 실행 권한 확인
ls -la .claude/hooks/pre-compact
```

예상: 실행 권한(`-rwxr-xr-x`)이 있어야 함

## Troubleshooting

### Hook이 실행되지 않음

**원인**: hooks가 실행 권한이 없거나 경로가 잘못됨

**해결**:
```bash
# 실행 권한 확인
ls -la .claude/hooks/

# 실행 권한 추가
chmod +x .claude/hooks/*
```

### settings.local.json이 적용되지 않음

**원인**: JSON 형식 오류 또는 Claude Code 재시작 필요

**해결**:
```bash
# JSON 형식 검증
cat .claude/settings.local.json | jq .

# Claude Code 재시작
```

### handoff 파일이 생성되지 않음

**원인**: handoff 디렉토리가 없거나 AI가 hook 메시지를 보지 못함

**해결**:
```bash
# 디렉토리 존재 확인
ls -la .claude/handoffs/

# 디렉토리 생성
mkdir -p .claude/handoffs

# index.md 초기화
cp agent-tools/.../assets/index-template.md .claude/handoffs/index.md
```

## Optional: Selective Hook Installation

모든 hook을 사용하지 않아도 됩니다. 필요한 것만 설치 가능:

### Only session-start

세션 시작 시 handoff 자동 로드만 원하는 경우:

```json
{
  "hooks": {
    "sessionStart": "bash .claude/hooks/session-start"
  }
}
```

### Only pre-compact

컨텍스트 압축 시에만 handoff 업데이트하는 경우:

```json
{
  "hooks": {
    "preCompact": "bash .claude/hooks/pre-compact"
  }
}
```

### All hooks (Recommended)

완전 자동화를 원하는 경우 모든 hooks 설치:

```json
{
  "hooks": {
    "sessionStart": "bash .claude/hooks/session-start",
    "sessionEnd": "bash .claude/hooks/session-end",
    "preCompact": "bash .claude/hooks/pre-compact"
  }
}
```

## Platform-Specific Notes

### Claude Code

- `settings.local.json`에 hooks 등록
- `.claude/hooks/` 디렉토리 사용

### Cursor

Cursor는 Claude Code와 다른 hook 시스템을 사용할 수 있습니다:

1. `.cursorrules` 파일에 handoff rules 추가 (hooks 대신)
2. 또는 Cursor의 custom commands 기능 사용

### Other AI Tools

hooks 스크립트는 독립적으로 실행 가능하므로:

```bash
# 수동 실행
bash .claude/hooks/session-start
bash .claude/hooks/session-end
```

## Best Practices

1. **팀 공유**: hooks 스크립트는 Git에 커밋하되, `settings.local.json`은 개인 설정
2. **점진적 도입**: 먼저 session-start만 사용해보고, 익숙해지면 나머지 추가
3. **커스터마이징**: 프로젝트에 맞게 hooks 스크립트 수정 가능
4. **백업**: hooks 변경 전 백업 권장

## Summary

```bash
# Quick setup (모든 hooks)
mkdir -p .claude/hooks .claude/handoffs
cp -r agent-tools/.../hooks/* .claude/hooks/
chmod +x .claude/hooks/*
cp agent-tools/.../assets/index-template.md .claude/handoffs/index.md

# settings.json 복사
cp agent-tools/.../hooks/settings.json .claude/settings.local.json
```

이제 handoff 시스템이 자동으로 작동합니다!

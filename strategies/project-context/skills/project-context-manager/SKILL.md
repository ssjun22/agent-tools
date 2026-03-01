---
name: project-context-manager
description: 작업 완료, 세션 종료, 프로젝트 상태 변경 시 프로젝트 컨텍스트 문서를 갱신할 때 사용한다. 변경사항을 정리해 사용자 확인 후 프로젝트 개요와 작업 상태를 업데이트하고 인덱스를 동기화한다.
---

# Project Context Update

## 목적

작업 내용을 `.claude/context/` 문서에 명시적으로 반영한다.
변경사항만 추려서 확인받는 방식으로 신뢰성과 효율성을 확보한다.

## 실행 절차

### 1. context/ 존재 확인

`.claude/context/` 디렉토리가 없으면 중단:
```
.claude/context/ 가 없습니다. /project-context-init 을 먼저 실행하세요.
```

### 2. 현재 파일 읽기

다음 파일을 읽어 현재 상태를 파악한다:
- `.claude/context/project.md`
- `.claude/context/status.md`

### 3. 업데이트 대상 확인

사용자에게 묻는다:
```
어떤 내용을 업데이트할까요?
1. project.md — 목적, Breaking Changes
2. status.md — 작업 상태 (진행 중/예정/완료)
3. 둘 다
```

### 4. 변경사항 정리 및 확인

이번 세션 내용을 바탕으로 변경된 내용만 추려서 제시한다.

```
[변경사항 — project.md]
- Breaking Changes 추가: {추가할 내용}
- 목적 수정: {변경 전} → {변경 후}

이대로 반영할까요? 수정이 필요하면 말씀해 주세요.
```

```
[변경사항 — status.md]
- 진행 중 → 진행 완료: {항목명}
- 진행 예정 → 진행 중: {항목명}
- 신규 추가 (진행 예정): {항목명}

이대로 반영할까요? 수정이 필요하면 말씀해 주세요.
```

수정 요청이 있으면 반영 후 재확인한다.
변경사항이 없는 파일은 skip한다.

### 5. 파일 저장

확인된 변경사항을 파일에 반영한다.
포맷은 `references/project-template.md`, `references/status-template.md` 를 참조한다.

### 6. index.md 동기화

`.claude/context/index.md` 를 갱신한다:
- Overview 섹션: 프로젝트명, 목적 한 줄
- Progress 섹션: 현재 진행 중인 작업 한 줄

### 7. 완료 안내

```
컨텍스트 업데이트 완료.
수정된 파일: {수정된 파일 목록}
```

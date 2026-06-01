# Plugins

This directory contains AI agent plugin packages.

Each plugin is a self-contained directory with its own README.md and optional components (rules/, skills/, agents/, hooks/).

## Available Plugins

### handoff

AI 에이전트 세션 간 컨텍스트 유지 및 협업을 위한 handoff 시스템.

**핵심 기능**:
- 세션 시작 시 자동 컨텍스트 로드
- Git 커밋 시 자동 handoff 업데이트
- 간결한 컨텍스트 전달 (~2000 토큰)

**포함 내용**:
- rules/: handoff 읽기/쓰기 규칙
- hooks/: pre-commit hook
- assets/: index 및 handoff 템플릿

**적용 대상**: Claude Code, Cursor, Codex, 모든 AI 에이전트

[자세한 내용 →](handoff/README.md)

---

### project-context

여러 독립 프로젝트를 오가며 작업할 때, 매번 맥락을 설명하지 않아도 AI가 프로젝트 상태를 빠르게 파악할 수 있도록 하는 컨텍스트 관리 플러그인.

**핵심 기능**:
- Lazy Loading: `index.md`만 자동 로드, 상세 파일은 선택적 참조
- 정적/동적 분리: `overview.md`(개요/스택)와 `progress.md`(진행 상황) 분리
- 자동 갱신: 세션 종료/PreCompact 시 `progress.md` 자동 업데이트

**포함 내용**:
- rules/: AI 동작 규칙 (CLAUDE.md에 추가)
- hooks/: `load-context`(SessionStart), `update-progress`(SessionEnd/PreCompact)
- skills/: `project-context-init` — 새 프로젝트 context/ 초기화
- assets/: index, overview, progress 템플릿

**적용 대상**: 여러 프로젝트를 관리하는 개발자

[자세한 내용 →](project-context/README.md)

---

See the parent skill's references/plugin-structure-guide.md for more information.

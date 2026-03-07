---
name: project-context-init
description: 현재 프로젝트에 .claude/context/ 구조를 초기화한다. index.md, project.md, status.md를 템플릿 기반으로 생성하고 hooks 설치를 안내한다.
---

# Project Context Init

## 목적

현재 프로젝트 레포에 `.claude/context/` 구조를 초기화한다.

## 실행 절차

1. `.claude/context/` 디렉토리 존재 여부 확인
   - 이미 있으면 덮어쓰기 전에 사용자에게 확인

2. 다음 파일과 디렉토리를 생성한다:
   - `.claude/context/index.md` — `references/index-template.md` 기반으로 생성
   - `.claude/context/project.md` — `references/project-template.md` 기반으로 생성
   - `.claude/context/status.md` — `references/status-template.md` 기반으로 생성
   - `.claude/context/refs/` — 빈 디렉토리 생성

3. 사용자에게 안내:
   ```
   .claude/context/ 초기화 완료.

   채워야 할 파일:
   - project.md: 목적, Breaking Changes, 도메인, 외부 링크
   - status.md: 현재 업무 목록
   - index.md: 파일 추가 시 목록과 참조 시점 업데이트

   참조 문서 추가 시:
   - refs/ 에 파일 생성 후 index.md에 등록

   hooks 미설치 시:
   - agent-tools/plugins/project-context/hooks/load-context → .claude/hooks/ 복사
   - agent-tools/plugins/project-context/settings.json → .claude/settings.local.json 복사
   - chmod +x .claude/hooks/load-context
   ```

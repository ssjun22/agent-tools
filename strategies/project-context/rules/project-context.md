# Project Context Rules

이 프로젝트의 컨텍스트는 `.claude/context/` 디렉토리에서 관리됩니다.
`.claude/context/` 디렉토리가 없으면 이 규칙을 무시합니다.

## 컨텍스트 로드

`.claude/context/index.md` 를 읽고 사용자에게 3줄 이내로 요약합니다:

```
[컨텍스트 로드됨]
프로젝트: {프로젝트명} — {목적 한 줄}
진행 중: {진행 중인 작업 한 줄}
```

상세 정보가 필요하면 `project.md` 또는 `status.md` 를 참조합니다.

## 파일별 역할

| 파일 | 성격 | 갱신 주체 |
|------|------|-----------|
| `context/index.md` | 진입점, 요약 | `/project-context-update` 실행 시 자동 동기화 |
| `context/project.md` | 정적 — 프로젝트 개요, 도메인, 아키텍처 결정 | `/project-context-update` |
| `context/status.md` | 동적 — 작업 상태 목록 | `/project-context-update` |

`context/`는 상태 정보, `CLAUDE.md`는 규칙/지침 — 역할을 혼용하지 않습니다.

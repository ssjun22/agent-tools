# agent-tools

Claude Code용 재사용 스킬·에이전트·규칙 중앙 저장소.
여기서 관리하고, 심링크로 각 프로젝트 레포의 `.claude/`에 배포한다.

## 디렉토리 구조

```
agent-tools/
├── agents/      # 서브에이전트 정의 (.md, YAML frontmatter)
├── skills/      # 스킬 (카테고리/스킬명/SKILL.md + scripts·references·assets)
│   ├── dev/         # 개발 보조 (code-reviewer, git-commit-helper, tdd, …)
│   ├── log/         # 업무 기록 (daily-work-log-manager, articles-summarizer, …)
│   ├── meta/        # 도구 관리 (skill-creator, agent-tools-linker, session-handoff, …)
│   ├── pipeline/    # task-pipeline 코드 변경 하네스
│   ├── planning/    # 설계 인터뷰 (brainstorming, grill-me)
│   ├── project/     # 프로젝트 QA (confluence-project-qa)
│   └── design/      # UI/UX (ui-ux-pro-max)
├── rules/       # CLAUDE.md에 병합해 쓰는 행동 규칙
└── plugins/     # 스킬·에이전트·규칙 묶음 매니페스트 (plugin.json)
```

## 배포 방법

**개별 스킬/에이전트 연결** — `agent-tools-linker` 스킬:

```
/agent-tools-linker skill git-commit-helper my-app
/agent-tools-linker agent researcher my-app
```

**묶음 배포** — `agent-plugin-manager` 스킬 (plugin.json이 선언한 의존성을 일괄 심링크):

```
/agent-plugin-manager karpathy-coding-guide my-app
```

레포 별칭은 각 스킬의 `assets/config.local.json`에서 관리한다.

## 주요 자산

| 자산 | 설명 |
|---|---|
| `skills/pipeline/task-pipeline` | 코드 변경 하네스 — 수렴→기준→plan→동결→루프→검수. 결정론 판정은 `core.sh` 소유 |
| `agents/{explorer,planner,generator,refactorer}` | task-pipeline 단계별 crew |
| `agents/context-doc-updater` | 세션에서 코드로 도출 불가한 컨텍스트를 문서에 통합 (propose/apply 2모드) |
| `agents/researcher` | 웹 조사 + 출처 필수 요약 |
| `skills/meta/skill-creator` | 스킬 제작·평가·설명문 최적화 루프 |
| `skills/meta/session-handoff` | 세션 인수인계 문서 생성 (라벨·검증·소비 규약 포함) |

## 작성 규약

- 스킬: 결정론 작업(파싱·날짜 연산·검증)은 `scripts/`로, 긴 참조 문서는 `references/`로,
  출력 템플릿은 `assets/`로 분리한다. SKILL.md는 워크플로우와 판단 기준만 담는다.
- 에이전트: YAML frontmatter(name·description·tools·model) 필수.
- 개인 설정(`config.json`, `config.yaml`, `config.local.json`)은 gitignore 대상 —
  `.example` 파일을 함께 커밋한다.

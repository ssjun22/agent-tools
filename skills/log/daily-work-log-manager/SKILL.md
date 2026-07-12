---
name: daily-work-log-manager
description: Daily work journal manager with automatic TODO/Issue/Notes tracking from previous day. This skill should be used when users want to create daily work logs in Obsidian vault, migrate incomplete tasks from yesterday, or set up structured daily notes. Triggered when users request to create today's work log, start daily journal, or initialize daily work notes.
allowed-tools: Read, Write, Bash
---

# Daily Work Log Manager

Obsidian vault(`Daily Notes/YYYY/M월/N주차/YYYY-MM-DD.md`)에 오늘의 업무 일지를 생성한다.
어제(없으면 가장 최근) 일지의 미완료 TODO/Issue/Note를 이월하는 작업은 **`scripts/migrate.py`가 결정론으로 전담**한다
— 파싱, 날짜 연산, 14일 경과 backlog 분류, 트리 이동을 LLM이 직접 수행하지 않는다.
이월 규칙의 정본은 `scripts/migrate.py` 상단 docstring이다 (여기 재서술하지 않음).

## Workflow

### Step 1: config 확인

스킬 디렉토리의 `config.json`이 있는지 확인한다.

```json
{
  "vault_path": "/absolute/path/to/Obsidian Vault",
  "daily_notes_path": "Daily Notes",
  "project_sections": ["프로젝트A", "프로젝트B", "기타"]
}
```

없으면(최초 실행) 사용자에게 세 값을 물어 위 형식으로 생성한다. 물을 것:
vault 절대 경로, Daily Notes 폴더명(기본값 "Daily Notes"), TODO 프로젝트 섹션 목록.
`config.json.example`을 참고용으로 보여줘도 좋다.

### Step 2: dry-run으로 초안 생성

```bash
python3 scripts/migrate.py --config <스킬디렉토리>/config.json
```

출력 JSON:

- `summary` — 대상 날짜, 이월 소스(`yesterday`/`recent`/`template`), 섹션별 이월 건수, backlog로 이동한 항목
- `today_path` — 오늘 파일 경로
- `draft` — 오늘 파일 전체 초안

`summary`를 사용자에게 보기 좋게 요약해 보여준다. 예:

```
📋 2026-07-11에서 이월: TODOs 4 · Backlogs 3 · Issues 2 · Notes 2
   Backlogs 이동(14일 경과): 코드 리뷰
```

`{"error": ...}`가 나오면 원인(설정 오류, 소스 파일 파싱 실패 등)을 사용자에게 알리고 중단한다.
소스 파일 형식이 깨져 파싱이 실패하는 경우, 사용자에게 해당 파일 수정을 권하거나
동의를 받아 `draft` 없이 기본 템플릿으로 진행한다.

### Step 3: 파일 저장

```bash
python3 scripts/migrate.py --config <...>/config.json --write
```

- 성공(`"written": true`) → Step 4로.
- `{"error": "EXISTS"}` (exit 3) → 오늘 파일이 이미 존재한다. 사용자에게 덮어쓸지 확인 받고,
  승인 시에만 `--write --force`로 재실행한다. 거부하면 기존 파일을 유지하고 종료.

### Step 4: 완료 보고

```
✅ 오늘 업무 일지 생성: Daily Notes/YYYY/M월/N주차/YYYY-MM-DD.md
이월: TODOs N · Backlogs N · Issues N · Notes N
```

이월 결과가 사용자 기대와 다르다는 피드백이 오면(예: 특정 항목 누락),
초안을 직접 고치지 말고 소스 파일의 형식 문제인지 확인한 뒤 파일을 Edit으로 보정한다.

## 산출 파일 구조

섹션 순서: `TODOs → Meetings → Issues → Notes → Articles → Retrospect → Backlogs(항목 있을 때만)`.
Meetings/Articles/Retrospect는 이월되지 않고 항상 새로 시작한다.
정적 골격은 `assets/default-template.md`가 정본이다.

## Troubleshooting

- **Python 없음** → Python 3.6+ 필요 (표준 라이브러리만 사용, 외부 의존성 없음)
- **vault 경로 오류** → config.json의 `vault_path`가 절대 경로인지 확인
- **주말 공백 등으로 어제 파일 없음** → 자동으로 가장 최근 일지에서 이월 (`source_kind: "recent"`)
- **이전 일지가 하나도 없음** → 기본 템플릿으로 생성 (`source_kind: "template"`)

## Resources

- `scripts/migrate.py` — 이월 + 오늘 파일 생성 (규칙 정본은 파일 상단 docstring)
- `scripts/date_helper.py` — 날짜/경로 계산 (migrate.py가 내부에서 사용, 단독 실행도 가능)
- `assets/default-template.md` — 일지 골격 템플릿
- `config.json.example` — 설정 예시

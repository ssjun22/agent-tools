AI 에이전트를 위한 재사용 가능한 프롬프트, 스킬, 에이전트 정의 및 플러그인을 관리하는 중앙 저장소입니다. 스킬을 **사용**하려면 사용자 프로젝트의 `.claude/skills/`에 심볼릭 링크나 복사본을 생성해야 합니다.

**핵심 원칙**: 재사용성 우선 - 공통 프롬프트와 스킬은 여러 에이전트와 프로젝트에서 참조됩니다.

**주요 작업 영역**: `skills/shared/`, `agents/shared/`, `plugins/` — 이 세 디렉토리가 가장 활발하게 작업되는 핵심 영역입니다. 새 스킬/에이전트/플러그인 작업 시 이 디렉토리들을 우선 탐색하세요.

## Directory Structure

- **`agents/`** - 에이전트 정의 (`shared/`: 범용, `local/`: 프로젝트 특화)
- **`prompts/`** - 공통 프롬프트 (`with_code/`, `without_code/`, `react/`, `_root/`)
- **`skills/`** - Claude Code 스킬 (`shared/`, `archived/`, `reference/`)
- **`plugins/`** - 프로젝트에 적용하면 AI 동작을 확장하는 패키지

### Plugins (`plugins/`)

각 플러그인은 `.claude/`에 배치할 수 있는 구성요소(rules, hooks, agents, skills, settings)를 목적별로 조합합니다. 프로젝트에 적용할 때는 플러그인의 구성요소를 프로젝트 `.claude/` 하위에 복사하거나 심볼릭 링크합니다.

개별 플러그인 목록은 `plugins/` 하위 디렉토리와 각 플러그인의 `README.md`를 참조하세요.

### Skills 카테고리 (`skills/shared/`)

- **`design/`** - UI/UX 디자인
- **`dev/`** - 개발 도구 (코드 리뷰, 커밋, 템플릿 등)
- **`log/`** - 기록/로그/회의
- **`meta/`** - 스킬 자체 개발/AI 설정
- **`planning/`** - 계획/문서 작성
- **`project/`** - 프로젝트/이슈 관리

개별 스킬 목록은 하위 디렉토리를 탐색하고, 각 스킬의 `SKILL.md`를 참조하세요.

### Skill Structure

```
skill-name/
├── SKILL.md           # YAML frontmatter + 사용법
├── references/        # 스킬 참조 문서
├── assets/            # 템플릿, 예제 파일
└── scripts/           # 자동화 스크립트 (선택사항)
```

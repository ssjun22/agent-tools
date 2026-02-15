## OpenSpec (Spec Driven Development)

이 프로젝트는 OpenSpec 기반 SDD를 따른다. `openspec/`은 이 프로젝트의 single source of truth이다.

**openspec/ 구조:**
- `openspec/specs/{domain}/spec.md` — main spec. 현재 시스템 동작을 정의하는 requirements와 scenarios
- `openspec/changes/{change-name}/` — 활성 변경. proposal.md(왜), specs/(delta spec), design.md(어떻게), tasks.md(단계) 포함
- `openspec/changes/archive/` — 완료된 변경 이력

**delta spec**: change 폴더의 specs/에 위치하며 main spec 대비 ADDED/MODIFIED/REMOVED 섹션으로 변경사항을 기술한다. `/opsx:archive` 시 main spec에 자동 병합된다.

### 참조 규칙 (Lazy Loading)

1. **질문/구현 요청 시**: 먼저 `openspec/specs/`와 `openspec/changes/`의 폴더 목록을 확인하라
2. **관련 도메인이 있으면**: 해당 폴더의 `spec.md`, `proposal.md`, `tasks.md`를 읽어 맥락을 파악하라
3. **관련 도메인이 없으면**: openspec 참조 불필요
4. **구현 시**: 반드시 해당 스펙의 requirements/scenarios를 기준으로 구현하라
5. **전체 파일을 한번에 읽지 마라** — 폴더명으로 판단 후 필요한 파일만 읽어라

### 동기화 규칙

- **스펙 변경 요청을 받으면**: spec 파일을 직접 수정하지 마라. 반드시 `/opsx:new`로 새 change를 생성하여 정식 flow를 따르라
- **코드 변경 후**: 해당 변경이 기존 스펙에 영향을 주면 반드시 알려라
  - "이 변경은 openspec/specs/{domain}의 스펙에 영향을 줍니다. `/opsx:new`로 스펙 업데이트가 필요합니다."
- **코드와 스펙이 불일치하는 경우**: 스펙이 기준이다. `/opsx:new` flow로 코드를 스펙에 맞춰 수정하라. 코드에 스펙을 맞추지 마라. 불일치를 발견하면 명시적으로 알리고 `/opsx:verify`를 권장하라.
- **기존 코드에서 spec을 생성할 때(Brownfield)**: `/opsx:seed` 후 `/opsx:audit-spec`을 **반드시 수행**하라. audit 결과 이슈/행동 변경이 필요하면 `/opsx:new`로 변경 flow에 진입하라.

### 스펙 변경 판단 기준

| 변경 규모 | 행동 |
|----------|------|
| 큰 변경 (새 기능, 스펙 추가/삭제) | `/opsx:new` → `/opsx:ff` → `/opsx:apply` → `/opsx:verify` → `/opsx:archive` |
| 중간 변경 (기존 요구사항 수정) | `/opsx:new` → `/opsx:ff` → `/opsx:apply` → `/opsx:verify` → `/opsx:archive` |
| 브라운필드 문서화 (기존 코드 기반) | `/opsx:seed` → `/opsx:audit-spec`(필수) → (필요 시) `/opsx:new` → `/opsx:ff` → `/opsx:apply` → `/opsx:verify` → `/opsx:archive` |
| 작은 변경 (오타, 명확화 수준) | `openspec/specs/` 직접 수정 OK |

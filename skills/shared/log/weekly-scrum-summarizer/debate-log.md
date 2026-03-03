# Debate Log — weekly-scrum-summarizer

---

### Round 1 - Critic

| # | 차원 | 심각도 | 위치 | 문제 | 개선 방향 |
|---|------|--------|------|------|-----------|
| 1 | Context Economy & Progressive Disclosure | High | SKILL.md 전체 | [NEW] SKILL.md가 343줄로 과도하게 비대함. Step 2~4의 파싱 로직(유사도 계산 공식, 예시 YAML 블록, Tips 12개)이 Claude가 매번 소비하는 컨텍스트를 불필요하게 키움. DESIGN.md가 별도 존재함에도 구현 세부사항이 중복 기술됨. | 파싱 알고리즘(Step 2), 중복 감지 로직(Step 4), Tips 섹션을 DESIGN.md 또는 별도 references/ 파일로 분리하고 SKILL.md에는 핵심 절차(What, When, 결정 지점)만 잔류 |
| 2 | Context Economy & Progressive Disclosure | Medium | Step 4 중복 감지 섹션 | [NEW] "Benefits", "When to trigger", "Important notes"가 3회 반복 기술됨. 같은 내용(유저 확인 필수, sub-item만 처리)이 Step 4 여러 위치에 분산되어 중복. | 해당 항목들을 단일 블록으로 통합하고 나머지 제거 |
| 3 | Packaging & Trigger Fidelity | Medium | frontmatter description | [NEW] description이 "Scrum Master needs to create or update weekly team summaries from Slack scrum thread messages"로 역할이 특정 직함(Scrum Master)에 종속되어 있고, 자동 활성화 판단 신호("Slack thread text 제공 시")는 존재하지만 "한 주 요약", "수도일", "금요일" 키워드가 description이 아닌 본문 "When to Use"에만 명시됨. | description에 트리거 키워드("한 주 요약", "수/금 업데이트")를 직접 포함시켜 자동 활성화 판단 신뢰도 향상 |
| 4 | Packaging & Trigger Fidelity | Low | 디렉토리 구조 | [NEW] 표준 구조(`references/` 디렉토리)가 없음. DESIGN.md는 루트에 위치하나 assets/, scripts/와 병렬로 분류 기준이 불명확. config.yaml과 config.yaml.example이 루트에 혼재. | `references/` 디렉토리 도입하여 DESIGN.md 이동, config 파일은 assets/config/ 하위로 정리 |
| 5 | Role Focus & Scope Control | High | Step 4 전체 | [NEW] "중복 서브아이템 감지 및 통합"은 문서 편집(1차 역할)과 독립적인 별도 기능임. 이 로직은 50% Jaccard 유사도 계산, 배치 처리, 진행 단계 통합 감지 등 복잡도가 높아 스킬 범위를 크게 확장시킴. 실패 시 전체 파이프라인 블로킹 위험. | Step 4를 Non-goal로 격리하거나, 별도 선택적 플래그(`--deduplicate`)로 opt-in 방식으로 분리. Non-goals 섹션 명시 필요. |
| 6 | Role Focus & Scope Control | Medium | SKILL.md 전체 | [NEW] Non-goals 섹션이 없음. "이 스킬이 하지 않는 것"이 명시되지 않아 역할 경계가 열려 있음. 예: 팀원 추가/삭제, 과거 문서 소급 수정, Jira 연동 등이 범위에 포함될지 불분명. | "## Non-goals" 섹션 추가. 최소한 "기존 main item 수정 안 함", "과거 주차 소급 없음" 등 명시 |
| 7 | Human-in-the-loop Checkpoints | Blocker | Step 2 파싱 / Step 3 CREATE | [NEW] 프로젝트 매칭 실패("No match → ask user")는 조건이 명시되어 있으나, **인덴테이션 없는 입력**("No indentation → infer from context or ask user")의 경우 "infer from context" 경로에서 사용자 확인 없이 추론 후 진행하는 암묵적 자동화가 존재함. 파싱 결과가 틀릴 경우 문서 오염. | 인덴테이션 불명확 시 **항상** 파싱 결과 미리보기를 제시하고 명시적 승인을 요구하는 체크포인트 추가 |
| 8 | Human-in-the-loop Checkpoints | High | Step 3 UPDATE, Step 5 설정 | [NEW] UPDATE 모드에서 기존 문서를 덮어쓰기 전 "현재 파일 내용 확인 후 진행하겠습니까?" 체크포인트가 없음. 파일이 이미 존재할 경우 자동으로 읽고 수정하여 저장하는 흐름이 단절 없이 이어짐. | UPDATE 실행 전 파일 경로와 마지막 수정일 표시 후 사용자 승인 요구 |
| 9 | Verification, Determinism & Observability | High | Step 4 유사도 계산 | [NEW] Jaccard 유사도 50% 임계값과 stop-word 목록이 SKILL.md에 하드코딩되어 있으나, 실제 LLM이 이 계산을 수행하므로 동일 입력에 대한 유사도 결과가 세션마다 다를 수 있음(비결정적). 임계값 경계(49% vs 51%)에서 다른 결과를 낼 위험. | 유사도 판단 기준을 "키워드 중복 N개 이상"처럼 결정적 규칙으로 단순화하거나, scripts/의 Python 스크립트에 위임하여 LLM 비결정성 제거 |
| 10 | Verification, Determinism & Observability | High | Step 6 출력 / 전체 플로우 | [NEW] 성공 완료 조건이 "파일 저장"으로만 정의되어 있음. "몇 명이 파싱되었는지", "몇 개 항목이 추가되었는지"에 대한 검증 가능한 수치 기준이 없음. 파싱 실패(0명 파싱)해도 Step 6 출력이 성공처럼 보일 수 있음. | 완료 보고에 "파싱된 팀원 수 / 예상 팀원 수", "추가된 항목 수" 포함. 파싱 결과가 0명이면 에러로 처리하는 guard 조건 명시 |
| 11 | Verification, Determinism & Observability | Medium | 파일 경로 계산 (Step 1) | [NEW] 주차 계산 공식("매월 1일이 속한 주 = 1주차")이 SKILL.md에만 텍스트로 기술되어 있음. LLM이 이를 직접 계산하면 경계 날짜(월말/월초, 연말)에서 오류 가능. scripts/update_weekly_summary.py가 있으나 SKILL.md에서 이 스크립트를 실제로 호출하라는 지시가 없음. | SKILL.md에서 주차 계산 시 반드시 scripts/update_weekly_summary.py를 호출하도록 명시 |
| 12 | Context Economy & Progressive Disclosure | Medium | Step 5 설정 섹션 | [NEW] config.yaml 구조 전체가 SKILL.md에 인라인으로 포함됨(config.yaml.example이 별도 파일로 존재함에도). 두 파일 간 동기화 부담 발생 가능. | config 구조 설명을 "config.yaml.example 참조"로 대체하고 SKILL.md에서는 핵심 키(`vault_path`, `members`, `project_keywords`)만 언급 |

**수렴 신호**: [많은 근본 문제]

- 구조적 문제(SKILL.md 비대화, Non-goals 부재, scripts 미연동)와 신뢰성 문제(비결정적 유사도, HitL 체크포인트 누락)가 복합적으로 존재함.
- Step 4(중복 감지)의 범위 적합성 재검토와 UPDATE 모드의 사전 확인 체크포인트 추가가 최우선 과제.

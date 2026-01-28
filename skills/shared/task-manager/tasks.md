# 프로젝트 업무 리스트

> 이 파일은 현재 진행 중인 업무와 완료된 업무를 관리합니다.

---

## 📋 진행 중인 업무

### [#1] 새 에이전트(루브릭 제거 버전) 개발
- **담당자**: JIRA_ASSIGNEE_D
- **보고자**: JIRA_ASSIGNEE_D
- **우선순위**: 높음
- **작업 기한**: 2026-02-12
- **Jira Parent**: 없음
- **상태**: OPEN
- **Jira Key**: AR-202
- **연관 업무**: #3, #5
- **설명**:
  - **목표**: 기존 프롬프트 기반 에이전트를 수정하여 새로운 평가 방식 구현
  - **배경**: 기존 자세한 규칙 프롬프팅이 평가에 적절한지 확신 불가 → LLM 자체 판단력 활용 시도
  - **상세 내용**:
    - [ ] 기존 프롬프트 수정 (에이전트 구조 변경 가능)
    - [ ] 두 에이전트 분리 및 개발 (루브릭 제거 / 루브릭 기반 가감점)
    - [ ] 결과 취합 로직 구현 및 비율 조정 기능 추가
    - [ ] 200개 샘플 데이터로 테스트 실행 및 결과 저장
  - **산출물**: `llm-server/temp_score_test/data/new_agent_results.json`
  - **관련 파일**:
    - `llm-server/llm/agents/*/format_scores_generator_parallel`
    - `llm-server/temp_score_test/submission_list.csv`

### [#2] 키위티 점수 매핑 함수 개발
- **담당자**: JIRA_ASSIGNEE_D
- **보고자**: JIRA_ASSIGNEE_D
- **우선순위**: 중간
- **작업 기한**: 없음
- **Jira Parent**: 없음
- **상태**: OPEN
- **Jira Key**: AR-205
- **연관 업무**: #3
- **설명**:
  - **목표**: 에이전트 결과를 키위티 점수 체계(A+, B, D+ 등)로 변환하는 매핑 함수 개발
  - **배경**: 키위티와 자체 에이전트 간의 평가 점수 기준 정렬 필요
  - **상세 내용**:
    - [ ] 키위티 화면 분석하여 점수 체계 추론
    - [ ] 기존/새 에이전트 점수 → 키위티 점수 매핑 함수 작성
    - [ ] 샘플 데이터로 매핑 결과 검증
  - **산출물**: `llm-server/temp_score_test/scripts/mapping_functions.py`

### [#3] Keewi-T 결과 분석 환경 구축 및 3-way 비교 분석
- **담당자**: JIRA_ASSIGNEE_D
- **보고자**: JIRA_ASSIGNEE_D
- **우선순위**: 중간
- **작업 기한**: 없음
- **Jira Parent**: 없음
- **상태**: OPEN
- **Jira Key**: AR-206
- **연관 업무**: #1, #2
- **설명**:
  - **목표**: 분석 환경을 정리하고 세 가지 평가 결과를 비교 분석하여 새 에이전트 성능 검증
  - **상세 내용**:
    - [ ] 새 에이전트 및 점수 매핑 함수 개발 완료 후 진행 권장
    - [ ] Keewi-T 결과(JSON)를 Excel/CSV로 변환
    - [ ] 분석 스크립트 및 결과 관리를 위한 폴더 구조(scripts, data, results) 정리
    - [ ] 세 가지 결과(Keewi-T, 기존/새 에이전트) 통합 테이블 구축 및 통계 분석
    - [ ] 결과 시각화 및 분석 리포트 작성
  - **관련 파일**:
    - `llm-server/temp_score_test/keewi_results.json`
    - `llm-server/temp_score_test/data/new_agent_results.json`
  - **산출물**:
    - `llm-server/temp_score_test/data/keewi_results.csv`
    - `llm-server/temp_score_test/results/comparison_report.md`
    - `llm-server/temp_score_test/scripts/analyze_comparison.py`

### [#4] 차이홍 톡톡 LLM 서버 셋업 및 요구사항 분석
- **담당자**: JIRA_ASSIGNEE_D
- **보고자**: JIRA_ASSIGNEE_D
- **우선순위**: 높음
- **작업 기한**: 없음
- **Jira Parent**: 없음
- **상태**: OPEN
- **Jira Key**: AR-207
- **연관 업무**: 없음
- **설명**:
  - **목표**: 차이홍 톡톡 프로젝트 요구사항 분석 및 최적 기술 스택 선정
  - **상세 내용**:
    - [ ] 상세 요구사항 분석 및 에이전트 구조 설계
    - [ ] Google ADK vs AI SDK 기술 스택 검토
    - [ ] 선정된 기술 스택 기반 초기 환경 셋업
  - **산출물**: 요구사항 분석 문서, 초기 프로젝트 스켈레톤 코드

### [#5] 루브릭 에이전트 고도화
- **담당자**: JIRA_ASSIGNEE_D
- **보고자**: JIRA_ASSIGNEE_D
- **우선순위**: 중간
- **작업 기한**: 없음
- **Jira Parent**: 없음
- **상태**: OPEN
- **Jira Key**: AR-208
- **연관 업무**: #1과 병행 가능
- **설명**:
  - **목표**: 기존 루브릭 기반 가감점 에이전트의 로직 고도화 및 정확도 개선
  - **상세 내용**:
    - [ ] 기존 루브릭 기준 정제 및 감점 로직 최적화
    - [ ] 성능 테스트 및 새 에이전트와의 통합 테스트
  - **관련 파일**: `llm-server/llm/agents/*/format_scores_generator_parallel`

---

## ✅ 완료된 업무

### [#완료1] Keewi-T 샘플 데이터 평가 결과 수집 (Playwright 자동화)
- **담당자**: JIRA_ASSIGNEE_D
- **보고자**: JIRA_ASSIGNEE_D
- **우선순위**: 중간
- **작업 기한**: 2026-01-26
- **완료일**: 2026-01-26
- **Jira Key**: AR-209
- **상태**: 완료
- **연관 업무**: 없음
- **설명**:
  - **수행 내용**: 약 200개 샘플 데이터에 대해 Keewi-T 웹사이트에서 자동 평가 수행 및 결과 수집
  - **결과**: 총점 및 항목별 점수를 JSON 파일로 저장 완료
  - **산출물**: `/tmp/playwright-keewi-automation.js`, `keewi_results.json`


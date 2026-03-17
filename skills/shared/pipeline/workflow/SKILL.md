---
name: workflow
description: "개발 세션 워크플로우 가이드. 체크리스트를 주입하여 메인 AI가 단계별로 사용자를 안내한다."
argument-hint: "[interview|spec|design|build|check|review|docs|commit]"
---

# Workflow Guide

세션 시작 시 또는 사용자가 `/workflow`를 호출하면 아래 체크리스트를 기반으로 현재 위치를 파악하고 다음 단계를 안내한다.

## Command Arguments

```
/workflow [step-name]
```

- **step-name** (선택): 시작할 스텝 이름. 생략 시 1번부터 시작.

### 스텝 이름 매핑

| step-name | 시작 스텝 | 용도 |
|-----------|----------|------|
| `interview` | 3. @interviewer | 작업 선택 후 바로 인터뷰부터 |
| `spec` | 4a. @spec-writer (proposal) | 인터뷰 없이 스펙 작성부터 |
| `design` | 5. @designer | UI/UX 설계부터 |
| `build` | 6. @spec-builder | 스펙이 이미 있을 때 구현부터 |
| `check` | 7. @spec-checker | 구현 완료 후 검증부터 |
| `review` | 9. 코드 리뷰 | 검증 통과 후 리뷰부터 |
| `docs` | 10. @docs-updater | 문서 수정만 할 때 |
| `commit` | 11. @committer | 커밋만 할 때 |

### 사용 예시

| 호출 | 동작 |
|------|------|
| `/workflow` | 1번(작업사항 확인)부터 시작 |
| `/workflow build` | 6번(@spec-builder)부터 시작 — 스펙이 이미 있을 때 |
| `/workflow docs` | 10번(@docs-updater)부터 시작 — 문서 수정만 할 때 |
| `/workflow commit` | 11번(@committer)부터 시작 — 커밋만 할 때 |

### 시작 스텝 지정 시 동작

- 지정된 스텝 **이전 단계는 건너뛴다** (완료된 것으로 간주).
- 지정된 스텝부터 체크리스트를 이어서 진행한다.
- 자동 진행/멈춤 규칙은 동일하게 적용된다.

## 상태 파악

호출 시 아래 파일을 읽어 현재 위치를 판단한다:

| 파일                      | 확인 내용                                |
| ------------------------- | ---------------------------------------- |
| `docs/context/status.md`  | 진행 중/예정 작업, 마지막 업데이트       |
| `docs/context/project.md` | 도메인, 아키텍처 결정 (필요 시)          |
| `openspec/changes/`       | 활성 change 존재 여부 및 artifact 진행도 |
| `git status`              | 미커밋 변경사항 여부                     |

참고: 파일별 역할과 갱신 규칙은 `.claude/rules/project-context.md`를 따른다.

## 체크리스트

```
□ 1. 작업사항 확인 — status.md 읽고 진행 중/예정 항목 요약
□ 2. 작업 선택 — 기존 항목 선택 또는 새 작업 시작
□ 3. @interviewer — 내용 파악 + 브레인스토밍 + 스펙 논의
□ 4a. @spec-writer (proposal) — interviewer 결과 기반 proposal.md 생성 → 사용자 확인
□ 4b. @spec-writer (artifacts) — 확인된 proposal 기반 나머지 artifact 생성 (specs/, design.md, tasks.md)
□ 5. @designer — UI/UX 설계 (frontend 작업일 때만)
□ 6. @spec-builder — tasks 기반 구현
□ 7. @spec-checker — 테스트 + 검증
     → PASS: 9번으로
     → FAIL: 8번으로
□ 8. 이슈 수정 — 메인 대화 또는 @spec-builder 로 수정 후 7번(@spec-checker) 재실행
□ 9. 코드 리뷰 (병렬)
     9a. @code-reviewer — 코드 품질/보안/패턴 검사
     9b. @gemini-prompt-evaluator — ADK 프롬프트 품질 평가 (LLM 프롬프트 변경 시에만)
     → 둘 다 CLEAR: 10번으로
     → 하나라도 BLOCKED (CRITICAL): 4번(@spec-writer) 또는 6번(@spec-builder)으로
     → BLOCKED (HIGH): 6번(@spec-builder)으로
     → BLOCKED (MEDIUM): 메인 대화에서 수정 후 9번 재실행
□ 10. @docs-updater — docs/context/, openspec 문서 갱신
□ 11. @committer — 변경사항 커밋
```

## 자동 진행 규칙

각 에이전트는 output 마지막에 `Status: CLEAR` 또는 `Status: BLOCKED`를 반환한다.

- **CLEAR**: 문제 없음. 다음 스텝으로 자동 진행한다.
- **BLOCKED**: 문제 있음. 사용자에게 이유를 보여주고 멈춘다.

### 항상 멈추는 스텝

| 스텝          | 이유                                 |
| ------------- | ------------------------------------ |
| 2. 작업 선택  | 사용자가 직접 결정                   |
| 3. @interviewer | 요구사항 확정은 사용자 확인 필요     |
| 4a. @spec-writer (proposal) | proposal.md가 이후 artifact의 기반. 방향 확인 필요 |
| 8. 이슈 수정  | FAIL에서만 진입, 수정 방향 결정 필요 |

### 조건부 멈추는 스텝

| 스텝             | BLOCKED 조건                                       | 아니면 자동 진행                     |
| ---------------- | -------------------------------------------------- | ------------------------------------ |
| 1. 작업사항 확인 | —                                                  | → 2번 (목록 + "새 작업 시작" 선택지 제시) |
| 4b. @spec-writer (artifacts) | —                                        | → 5번                                     |
| 5. @designer | —                                                  | → 6번                                |
| 6. @spec-builder    | 테스트 실패, tasks 없음, 설계 모순                 | → 7번                                |
| 7. @spec-checker | CRITICAL 이슈 발견                                 | → 9번                                |
| 9a. @code-reviewer  | CRITICAL/HIGH/MEDIUM 이슈 발견                     | → (9b 결과와 합산)                    |
| 9b. @gemini-prompt-evaluator | CRITICAL/HIGH 이슈 발견 (LLM 프롬프트 변경 시에만) | → (9a 결과와 합산)                    |
| 9. 종합 판정       | 9a 또는 9b 중 하나라도 BLOCKED                     | → 10번                               |
| 10. @docs-updater | Breaking Changes 등 큰 변경                        | → 11번                               |
| 11. @committer   | 민감 파일 감지, 커밋 분리 필요                     | → 완료                               |

### 컨텍스트 전달

- 4a @spec-writer (proposal) 호출 시, @interviewer의 Phase 5 출력(확정된 요구사항, 결정 로그, 추천 다음 단계)을 Agent tool의 prompt에 원문 그대로 포함한다. 요약하지 않는다.
- 4b @spec-writer (artifacts) 호출 시, 4a에서 사용자가 확인한 proposal.md 내용을 포함한다.

## 행동 규칙

1. 사용자가 `/workflow`를 호출하면:
   - **step-name argument가 있으면**: 스텝 이름 매핑 테이블에서 해당 스텝을 찾아 시작점으로 설정하고, 이전 스텝은 ✅ 완료로 표시한다
   - **step-name argument가 없으면**: 위 파일들을 읽고 현재 상태를 요약한다
   - 체크리스트에서 현재 위치를 판단한다
   - 다음 단계와 실행 방법을 안내한다

2. CLEAR 신호를 받으면 사용자 확인 없이 다음 스텝을 실행한다.

3. 단계를 건너뛰어도 된다 — 사용자가 직접 특정 에이전트를 호출하면 그에 맞춰 체크리스트를 갱신한다

4. 체크리스트를 표시할 때 `.claude/workflow-timing.json`이 존재하면 읽어서 완료된 스텝 옆에 소요 시간을 표시한다.
   예: `✅ 3. @interviewer (2분 34초)`

5. 모든 단계가 완료되면:
   - "워크플로우 완료. 다음 작업은 /workflow 로 새로 시작하세요."

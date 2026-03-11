---
name: workflow
description: "개발 세션 워크플로우 가이드. 체크리스트를 주입하여 메인 AI가 단계별로 사용자를 안내한다."
---

# Workflow Guide

세션 시작 시 또는 사용자가 `/workflow`를 호출하면 아래 체크리스트를 기반으로 현재 위치를 파악하고 다음 단계를 안내한다.

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
□ 4. @spec-writer — interviewer 결과 기반 OpenSpec artifact 생성
□ 5. @designer — UI/UX 설계 (frontend 작업일 때만)
□ 6. @spec-builder — tasks 기반 구현
□ 7. @spec-checker — 테스트 + 검증
     → PASS: 9번으로
     → FAIL: 8번으로
□ 8. 이슈 수정 — 메인 대화 또는 @spec-builder 로 수정 후 7번(@spec-checker) 재실행
□ 9. @code-reviewer — 코드 품질/보안/패턴 검사
     → CLEAR: 10번으로
     → BLOCKED (CRITICAL): 4번(@spec-writer) 또는 6번(@spec-builder)으로
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
| 8. 이슈 수정  | FAIL에서만 진입, 수정 방향 결정 필요 |

### 조건부 멈추는 스텝

| 스텝             | BLOCKED 조건                                       | 아니면 자동 진행                     |
| ---------------- | -------------------------------------------------- | ------------------------------------ |
| 1. 작업사항 확인 | —                                                  | → 2번 (목록 + "새 작업 시작" 선택지 제시) |
| 4. @spec-writer  | spec seed 필요, 기존 spec 충돌, artifact 생성 실패 | → 5번 (frontend 작업) 또는 6번 (그 외)    |
| 5. @designer | —                                                  | → 6번                                |
| 6. @spec-builder    | 테스트 실패, tasks 없음, 설계 모순                 | → 7번                                |
| 7. @spec-checker | CRITICAL 이슈 발견                                 | → 9번                                |
| 9. @code-reviewer  | CRITICAL/HIGH/MEDIUM 이슈 발견                     | → 10번                               |
| 10. @docs-updater | Breaking Changes 등 큰 변경                        | → 11번                               |
| 11. @committer   | 민감 파일 감지, 커밋 분리 필요                     | → 완료                               |

### 컨텍스트 전달

@spec-writer 호출 시, @interviewer의 Phase 5 출력(확정된 요구사항, 결정 로그, 추천 다음 단계)을 Agent tool의 prompt에 원문 그대로 포함한다. 요약하지 않는다.

## 행동 규칙

1. 사용자가 `/workflow`를 호출하면:
   - 위 파일들을 읽고 현재 상태를 요약한다
   - 체크리스트에서 현재 위치를 판단한다
   - 다음 단계와 실행 방법을 안내한다

2. CLEAR 신호를 받으면 사용자 확인 없이 다음 스텝을 실행한다.

3. 단계를 건너뛰어도 된다 — 사용자가 직접 특정 에이전트를 호출하면 그에 맞춰 체크리스트를 갱신한다

4. 모든 단계가 완료되면:
   - "워크플로우 완료. 다음 작업은 /workflow 로 새로 시작하세요."

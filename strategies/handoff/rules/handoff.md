# Handoff Rules

현재 세션에서 분리하고 싶은 작업이 생겼을 때, handoff 문서를 생성하여 새 세션에서 이어받을 수 있도록 한다.

## `.claude/handoffs/` 디렉토리

`.claude/handoffs/`는 현재 세션에서 분리된 작업의 인수인계 문서를 보관하는 곳이다.

- 파일명: `YYYY-MM-DD-제목.md`
- 완료된 handoff는 수동으로 정리
- `.claude/context/`(프로젝트 상태)와 역할이 다름 — handoff는 작업 단위 인계 문서

## 자동 감지 트리거

사용자 메시지에 다음 표현이 감지되면 `handoff-creator` 에이전트를 백그라운드로 실행한다:

### 감지해야 하는 표현

- "이건 나중에 따로 처리하자"
- "별도 세션에서 보자 / 따로 보자"
- "지금은 넘어가고 / 일단 넘기고"
- "다음에 이어서 하자"
- "handoff 만들어줘 / handoff 문서 만들어줘"
- "다른 세션에서 처리할게"
- "이 문제는 따로 해결하자"

### 감지하지 않아야 하는 표현 (무시)

- 단순 작업 지시: "나중에 리팩토링하자" (일정 표현, 분리 의도 없음)
- 확인: "좋아", "계속 진행해"

## 실행 방법

```
Agent 도구 사용:
- subagent_type: "general-purpose"
- run_in_background: true
- prompt: handoff-creator.md 역할 + 현재 대화에서 분리할 작업 내용 포함
```

## 수동 호출

사용자가 명시적으로 요청하거나 `@handoff-creator`를 언급할 때도 동일하게 실행한다.

## 세션 시작 시

`.claude/handoffs/`에 `status: pending` 파일이 있으면 사용자에게 알린다:

```
미완료 handoff 문서가 있습니다: handoffs/YYYY-MM-DD-제목.md
이어서 작업하시겠어요?
```

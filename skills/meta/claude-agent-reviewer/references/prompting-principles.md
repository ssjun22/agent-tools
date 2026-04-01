# Claude Prompting Principles

리뷰 판정의 이론적 근거가 되는 Claude 프롬프팅 원칙.

> Source: [Claude Prompting Best Practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)

## 명확성과 직접성

- 구체적인 출력 형식과 제약을 명시한다
- 순서가 중요하면 번호 매긴 리스트를 사용한다
- Golden rule: 맥락 없는 동료에게 프롬프트를 보여줬을 때 혼란스럽다면, Claude도 혼란스럽다

## 동기 부여로 성능 향상

단순 지시보다 "왜 그렇게 해야 하는지" 설명하면 Claude가 목표를 더 잘 이해하고 일반화한다:

- ❌ "NEVER use ellipses"
- ✅ "Your response will be read aloud by a text-to-speech engine, so never use ellipses since the engine won't know how to pronounce them."

## 4.6 모델의 과잉 프롬프팅 방지

4.6 모델은 이전 모델보다 시스템 프롬프트에 훨씬 민감하다.
이전 모델에서 미트리거 방지를 위해 쓰던 강조가 과잉 트리거를 유발한다:

- ❌ "CRITICAL: You MUST use this tool when..."
- ✅ "Use this tool when..."
- 과잉 탐색이 지속되면 effort 파라미터를 낮추어 조절한다

## 긍정 프레이밍

출력 형식과 행동 규칙을 부정("하지 마라")보다 긍정("이렇게 해라")으로 기술한다.
프롬프트의 포매팅 스타일을 원하는 출력 스타일과 일치시킨다.

## 역할 정의

시스템 프롬프트 첫 부분에 전문성과 행동 방식을 1-2문장으로 명시한다.
구체적인 역할이 범용 역할보다 성능이 좋다 (최소한의 디테일이라도).

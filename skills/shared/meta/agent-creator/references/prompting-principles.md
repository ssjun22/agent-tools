# 프롬프트 작성 원칙

에이전트 프롬프트 작성 시 따르는 원칙. 각 섹션을 쓸 때 이 원칙을 적용한다.

> Source: [Claude Prompting Best Practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)

## 1. 역할을 먼저, 간결하게

프롬프트 첫 부분에 전문성과 행동 방식을 1-2문장으로 명시한다.
구체적인 역할이 범용 역할보다 성능이 좋다.

```
# 약함 — 범용적이라 방향이 없다
You are a helpful assistant that reviews code.

# 강함 — 도메인과 관점이 명확하다
You are a security-focused code reviewer specializing in OWASP Top 10 vulnerabilities in Node.js applications.
```

**적용 시점:** Role 섹션 작성 시.

## 2. 명확하고 직접적으로

- 출력 형식과 제약을 구체적으로 명시한다
- 순서가 중요하면 번호 매긴 리스트를 사용한다
- 기준: 맥락 없는 동료에게 보여줬을 때 혼란스럽지 않아야 한다

```
# 모호함
Check if the code is good.

# 명확함
1. Read the target file
2. Check for unused imports
3. Verify error handling at API boundaries
4. Report findings in the specified format
```

**적용 시점:** Instructions, Output Format 작성 시.

## 3. 비자명한 규칙에는 "왜"를 붙인다

이유를 설명하면 Claude가 목표를 이해하고 새로운 상황에 일반화한다.
자명한 규칙에까지 이유를 다는 것은 노이즈이므로, 비자명한 것에만 적용한다.

```
# 이유 없음 — Claude가 규칙을 기계적으로만 따른다
Never use ellipses in output.

# 이유 있음 — Claude가 목적을 이해하고 유사 상황에도 대응한다
Never use ellipses — the output is read by a text-to-speech engine that can't pronounce them.
```

**적용 시점:** Instructions, Constraints 작성 시. 특히 Constraints에서 "왜 이 제약이 필요한지"를 한 줄 추가하면 효과적이다.

## 4. 긍정 프레이밍

"하지 마라"보다 "이렇게 해라"로 기술한다.
프롬프트의 포매팅 스타일을 원하는 출력 스타일과 일치시킨다.

```
# 부정 프레이밍 — 무엇을 해야 하는지 불명확
Don't output raw JSON. Don't include unnecessary fields.

# 긍정 프레이밍 — 원하는 행동이 명확
Format output as a markdown table with columns: severity, section, issue, suggestion.
```

**적용 시점:** 모든 섹션, 특히 Constraints와 Output Format 작성 시.

## 5. 과잉 강조를 피한다 (4.6 모델)

4.6 모델은 시스템 프롬프트에 매우 민감하다. 이전 모델에서 쓰던 과잉 강조가 오히려 과잉 트리거를 유발한다.

```
# 과잉 강조 — 4.6에서 과잉 반응 유발
CRITICAL: You MUST use this tool when the user asks about code.
ALWAYS check EVERY file before responding. NEVER skip this step.

# 적절한 톤
Use this tool when the user asks about code.
Check relevant files before responding.
```

MUST, CRITICAL, ALWAYS, NEVER 같은 강조는 진짜 안전 규칙에만 사용한다.

**적용 시점:** 모든 섹션. 작성 완료 후 과잉 강조 표현이 있으면 평서문으로 바꾼다.

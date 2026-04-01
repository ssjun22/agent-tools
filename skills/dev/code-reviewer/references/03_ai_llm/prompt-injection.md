---
title: Prompt Injection Prevention
impact: HIGH
impactDescription: prevents malicious prompt manipulation
tags: security, prompt-injection, validation
---

## Prompt Injection Prevention

사용자 입력을 직접 프롬프트에 삽입하지 말고, sanitization과 분리를 수행합니다.

**Incorrect (사용자 입력 직접 삽입):**

```python
async def chat_with_bot(user_message: str):
    prompt = f"You are a helpful assistant.\n\nUser: {user_message}"
    # 사용자가 "Ignore previous instructions"를 입력하면 위험
    return await llm.generate(prompt)
```

**Correct (입력 sanitization 및 분리):**

```python
def sanitize_input(text: str) -> str:
    # 프롬프트 injection 키워드 필터링
    dangerous_phrases = [
        "ignore previous",
        "ignore above",
        "disregard",
        "new instructions"
    ]

    text_lower = text.lower()
    for phrase in dangerous_phrases:
        if phrase in text_lower:
            raise ValueError("Potentially malicious input detected")

    return text[:500]  # 길이 제한

async def chat_with_bot(user_message: str):
    sanitized = sanitize_input(user_message)

    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant. Only respond to user questions."
        },
        {
            "role": "user",
            "content": sanitized
        }
    ]

    return await llm.chat(messages)
```

**Note:** 시스템 프롬프트와 사용자 입력을 명확히 분리하는 것이 중요합니다.

---
title: Context Window Management
impact: MEDIUM
impactDescription: prevents context overflow errors
tags: context, tokens, management
---

## Context Window Management

컨텍스트 윈도우 크기를 동적으로 관리하여 오버플로우를 방지합니다.

**Incorrect (Context 초과 무시):**

```python
async def chat_with_history(messages: List[Dict], new_message: str):
    messages.append({"role": "user", "content": new_message})
    # 메시지가 계속 쌓이면 context limit 초과
    response = await llm.chat(messages)
    return response
```

**Correct (동적 컨텍스트 관리):**

```python
import tiktoken

def count_tokens(text: str, model: str = "gpt-4") -> int:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def trim_messages(
    messages: List[Dict],
    max_tokens: int = 8000,
    keep_system: bool = True
) -> List[Dict]:
    system_msg = messages[0] if keep_system and messages[0]["role"] == "system" else None
    conversation = messages[1:] if system_msg else messages

    total_tokens = 0
    trimmed = []

    # 최신 메시지부터 역순으로 추가
    for msg in reversed(conversation):
        msg_tokens = count_tokens(msg["content"])
        if total_tokens + msg_tokens > max_tokens:
            break
        trimmed.insert(0, msg)
        total_tokens += msg_tokens

    if system_msg:
        trimmed.insert(0, system_msg)

    return trimmed

async def chat_with_history(messages: List[Dict], new_message: str):
    messages.append({"role": "user", "content": new_message})

    # 컨텍스트 윈도우에 맞게 trim
    trimmed = trim_messages(messages, max_tokens=7000)

    response = await llm.chat(trimmed)
    return response
```

**Note:** 시스템 메시지는 항상 유지하고, 최신 대화 내용을 우선적으로 포함합니다.

---
title: System/User/Assistant Role Separation
impact: HIGH
impactDescription: provides clear context and improves response quality
tags: prompt, roles, context, llm
---

## System/User/Assistant Role Separation

System, User, Assistant 역할을 명확히 분리하여 컨텍스트를 구조화합니다.

**Incorrect (역할 구분 없이 단일 프롬프트):**

```python
async def get_recommendation(user_query: str):
    prompt = f"You are a helpful assistant. User asks: {user_query}"
    response = await llm.generate(prompt)
    return response
```

**Correct (명확한 역할 분리):**

```python
from typing import List, Dict

async def get_recommendation(user_query: str, context: Dict[str, Any]):
    messages = [
        {
            "role": "system",
            "content": "You are an AI assistant specialized in software architecture."
        },
        {
            "role": "user",
            "content": f"Context: {context}\n\nQuestion: {user_query}"
        }
    ]

    response = await llm.chat(messages)
    return response

async def classify_issue(issue_description: str):
    messages = [
        {
            "role": "system",
            "content": "You classify issues into: bug, feature, improvement, question."
        },
        {
            "role": "user",
            "content": "The login button doesn't work"
        },
        {
            "role": "assistant",
            "content": "Category: bug"
        },
        {
            "role": "user",
            "content": issue_description
        }
    ]

    return await llm.chat(messages)
```

**Note:** 역할 분리는 LLM이 컨텍스트를 더 잘 이해하도록 도와줍니다.
